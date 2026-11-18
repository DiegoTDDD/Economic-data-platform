"""Fetching and parsing the external sources, with retries for transient failures.

  - BCB SGS (Banco Central do Brasil): JSON list of {"data": "dd/mm/yyyy", "valor": "1,23"}
  - yfinance: a DataFrame whose columns may come as a MultiIndex, depending on the version

Parsing is separate from fetching so tests can feed recorded payloads
(tests/test_sources.py) without touching the network.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import date

import pandas as pd
import requests

log = logging.getLogger(__name__)

BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
RETRY_STATUS = {429, 500, 502, 503, 504}  # worth retrying; any other 4xx is a bug on our side
MAX_ATTEMPTS = 4
BACKOFF_SECONDS = 2.0  # waits 2, 4, 8 s between attempts

INDICATOR_COLUMNS = ["date", "indicator_name", "value"]


class SourceError(RuntimeError):
    """A source failed after every retry, or answered with something unusable."""


def with_retries(
    call: Callable[[], requests.Response],
    what: str,
    attempts: int = MAX_ATTEMPTS,
    backoff: float = BACKOFF_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> requests.Response:
    """Run an HTTP call; retry timeouts, connection errors and 429/5xx with exponential backoff."""
    for attempt in range(1, attempts + 1):
        try:
            response = call()
        except (requests.Timeout, requests.ConnectionError) as exc:
            reason = f"{type(exc).__name__}: {exc}"
        else:
            if response.status_code == 200:
                return response
            if response.status_code not in RETRY_STATUS:
                raise SourceError(f"{what}: HTTP {response.status_code} (not retried)")
            reason = f"HTTP {response.status_code}"
        if attempt == attempts:
            raise SourceError(f"{what}: failed after {attempts} attempts ({reason})")
        wait = backoff * 2 ** (attempt - 1)
        log.warning("%s: attempt %d/%d failed (%s); retrying in %.0fs",
                    what, attempt, attempts, reason, wait)
        sleep(wait)
    raise AssertionError("unreachable")


def parse_bcb(payload: list[dict], indicator: str) -> pd.DataFrame:
    """BCB SGS JSON -> date, indicator_name, value. Unparseable rows are dropped."""
    if not isinstance(payload, list):
        raise SourceError(f"{indicator}: expected a JSON list, got {type(payload).__name__}")
    df = pd.DataFrame(payload, columns=["data", "valor"])
    values = df["valor"].astype(str).str.replace(",", ".", regex=False)
    out = pd.DataFrame({
        "date": pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce").dt.date,
        "indicator_name": indicator,
        "value": pd.to_numeric(values, errors="coerce"),
    })
    return out.dropna(subset=["date", "value"]).reset_index(drop=True)


def fetch_bcb(session: requests.Session, code: int, indicator: str, start: date, end: date,
              sleep: Callable[[float], None] = time.sleep) -> pd.DataFrame:
    """One BCB SGS series between two dates."""
    params = {"formato": "json", "dataInicial": f"{start:%d/%m/%Y}",
              "dataFinal": f"{end:%d/%m/%Y}"}
    response = with_retries(
        lambda: session.get(BCB_URL.format(code=code), params=params, timeout=30),
        f"BCB series {code}", sleep=sleep,
    )
    return parse_bcb(response.json(), indicator)


def flatten_yfinance(raw: pd.DataFrame) -> pd.DataFrame:
    """yfinance output -> one row per day with Date, Close and (if present) Volume columns."""
    if raw.empty:
        raise SourceError("yfinance returned no rows")
    frame = raw.reset_index()
    if isinstance(frame.columns, pd.MultiIndex):  # newer yfinance: ("Close", "BTC-USD")
        frame.columns = [first or second for first, second in frame.columns]
    if "Close" not in frame.columns:
        raise SourceError(f"yfinance: no Close column in {list(frame.columns)}")
    return frame


def parse_yfinance_series(raw: pd.DataFrame, indicator: str) -> pd.DataFrame:
    """A yfinance price history -> date, indicator_name, value (closing price)."""
    frame = flatten_yfinance(raw)
    out = pd.DataFrame({
        "date": pd.to_datetime(frame["Date"], errors="coerce").dt.date,
        "indicator_name": indicator,
        "value": pd.to_numeric(frame["Close"], errors="coerce"),
    })
    return out.dropna(subset=["date", "value"]).reset_index(drop=True)


def parse_bitcoin(raw: pd.DataFrame) -> pd.DataFrame:
    """BTC-USD history from yfinance -> date, close_price, volume."""
    frame = flatten_yfinance(raw)
    volume = frame["Volume"] if "Volume" in frame.columns else 0
    out = pd.DataFrame({
        "date": pd.to_datetime(frame["Date"], errors="coerce").dt.date,
        "close_price": pd.to_numeric(frame["Close"], errors="coerce"),
        "volume": pd.to_numeric(volume, errors="coerce"),
    })
    return out.dropna(subset=["date", "close_price"]).reset_index(drop=True)


def download_yfinance(ticker: str, start: str, attempts: int = MAX_ATTEMPTS,
                      sleep: Callable[[float], None] = time.sleep) -> pd.DataFrame:
    """yf.download with retries: Yahoo often rate-limits or returns empty frames transiently."""
    import yfinance as yf

    for attempt in range(1, attempts + 1):
        try:
            raw = yf.download(ticker, start=start, progress=False, auto_adjust=False)
            flatten_yfinance(raw)  # raises SourceError if empty or malformed
            return raw
        except Exception as exc:  # noqa: BLE001 - yfinance raises many types
            if attempt == attempts:
                raise SourceError(
                    f"yfinance {ticker}: failed after {attempts} attempts: {exc}"
                ) from exc
            wait = BACKOFF_SECONDS * 2 ** (attempt - 1)
            log.warning("yfinance %s: attempt %d/%d failed (%s); retrying in %.0fs",
                        ticker, attempt, attempts, exc, wait)
            sleep(wait)
    raise AssertionError("unreachable")
