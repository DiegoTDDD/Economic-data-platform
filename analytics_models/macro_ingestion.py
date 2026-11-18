"""Ingest Brazilian macro indicators into gold_economic_indicators.

  - IPCA, monthly %           BCB SGS series 433
  - Unemployment rate, %      BCB SGS series 24369 (PNAD Continua)
  - USD/BRL exchange rate     yfinance USDBRL=X

One failing source does not block the others: the sources that answered are
replaced, the one that failed keeps its previous rows in Gold, and a warning
names it. Nothing is written if no source answered or the batch fails its
quality checks.
"""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics_models.gold import engine_from_env, replace_table  # noqa: E402
from analytics_models.quality import check_indicators  # noqa: E402
from analytics_models.sources import (  # noqa: E402
    SourceError,
    download_yfinance,
    fetch_bcb,
    parse_yfinance_series,
)

log = logging.getLogger(__name__)
START = date(2015, 1, 1)
BCB_SERIES = {433: "IPCA - Monthly (%)", 24369: "Unemployment Rate (%)"}
USD_BRL = "USD/BRL Exchange Rate (Purchase)"


def collect(session: requests.Session, end: date) -> tuple[pd.DataFrame, list[str]]:
    """Every source that answers, stacked; plus the names of those that failed."""
    frames, failed = [], []
    for code, name in BCB_SERIES.items():
        try:
            frames.append(fetch_bcb(session, code, name, START, end))
            log.info("%s: %d rows", name, len(frames[-1]))
        except SourceError as exc:
            log.error("%s", exc)
            failed.append(name)
    try:
        frames.append(parse_yfinance_series(download_yfinance("USDBRL=X", f"{START:%Y-%m-%d}"),
                                            USD_BRL))
        log.info("%s: %d rows", USD_BRL, len(frames[-1]))
    except SourceError as exc:
        log.error("%s", exc)
        failed.append(USD_BRL)
    if not frames:
        raise SourceError("no macroeconomic source answered")
    batch = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["date", "indicator_name"])
    return batch, failed


def ingest_macro_data() -> int:
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "User-Agent": "economic-data-platform"})
    batch, failed = collect(session, date.today())
    if failed:
        log.warning("loaded without: %s", ", ".join(failed))
    # Only the indicators in this batch are replaced; a source that failed keeps its history.
    return replace_table(engine_from_env(), "gold_economic_indicators", batch,
                         check_indicators(batch), partition_by="indicator_name")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ingest_macro_data()
