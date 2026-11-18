"""Parsing recorded source payloads, and the retry logic, without the network."""

import sys
import types
from datetime import date

import pandas as pd
import pytest
import requests

from analytics_models import sources
from analytics_models.sources import SourceError


class Response:
    def __init__(self, status, payload=None):
        self.status_code = status
        self._payload = payload

    def json(self):
        return self._payload


def scripted(*outcomes):
    """A call that returns or raises each outcome in turn."""
    outcomes = list(outcomes)

    def call():
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    return call


def test_bcb_payload_is_parsed_and_bad_rows_dropped():
    payload = [{"data": "01/01/2024", "valor": "0.42"}, {"data": "01/02/2024", "valor": "0,83"},
               {"data": "not a date", "valor": "1"}, {"data": "01/03/2024", "valor": ""}]
    df = sources.parse_bcb(payload, "IPCA - Monthly (%)")
    assert df["date"].tolist() == [date(2024, 1, 1), date(2024, 2, 1)]
    assert df["value"].tolist() == [0.42, 0.83]
    assert (df["indicator_name"] == "IPCA - Monthly (%)").all()


def test_bcb_payload_must_be_a_list():
    with pytest.raises(SourceError):
        sources.parse_bcb({"error": "Value(s) not found"}, "IPCA")


def test_transient_failures_are_retried_with_exponential_backoff():
    waits = []
    call = scripted(Response(503), requests.Timeout("slow"), Response(200, []))
    assert sources.with_retries(call, "BCB", sleep=waits.append).status_code == 200
    assert waits == [2.0, 4.0]


def test_client_errors_are_not_retried():
    waits = []
    with pytest.raises(SourceError, match="404"):
        sources.with_retries(scripted(Response(404)), "BCB", sleep=waits.append)
    assert waits == []


def test_gives_up_after_the_last_attempt():
    waits = []
    call = scripted(*[Response(429)] * 4)
    with pytest.raises(SourceError, match="4 attempts"):
        sources.with_retries(call, "BCB", sleep=waits.append)
    assert waits == [2.0, 4.0, 8.0]


def test_fetch_bcb_sends_the_date_range():
    seen = {}

    class Session:
        def get(self, url, params, timeout):
            seen.update(url=url, params=params)
            return Response(200, [{"data": "01/01/2024", "valor": "7.9"}])

    df = sources.fetch_bcb(Session(), 24369, "Unemployment Rate (%)", date(2015, 1, 1),
                           date(2026, 11, 18))
    assert seen["url"].endswith("bcdata.sgs.24369/dados")
    assert seen["params"]["dataInicial"] == "01/01/2015"
    assert seen["params"]["dataFinal"] == "18/11/2026"
    assert df["value"].tolist() == [7.9]


def yfinance_frame(multi: bool) -> pd.DataFrame:
    idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02"], name="Date")
    df = pd.DataFrame({"Close": [42000.0, None], "Volume": [10.0, 20.0]}, index=idx)
    if multi:  # newer yfinance: columns like ("Close", "BTC-USD")
        df.columns = pd.MultiIndex.from_tuples([(c, "BTC-USD") for c in df.columns])
    return df


@pytest.mark.parametrize("multi", [False, True])
def test_yfinance_output_is_flattened_either_way(multi):
    btc = sources.parse_bitcoin(yfinance_frame(multi))
    assert btc.to_dict("list") == {"date": [date(2024, 1, 1)], "close_price": [42000.0],
                                   "volume": [10.0]}
    fx = sources.parse_yfinance_series(yfinance_frame(multi), "USD/BRL")
    assert fx["value"].tolist() == [42000.0]


def test_empty_yfinance_output_is_an_error():
    with pytest.raises(SourceError):
        sources.parse_bitcoin(pd.DataFrame())


def test_yfinance_download_is_retried(monkeypatch):
    calls = []

    def download(ticker, start, progress, auto_adjust):
        calls.append(ticker)
        return pd.DataFrame() if len(calls) < 3 else yfinance_frame(True)

    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=download))
    waits = []
    raw = sources.download_yfinance("BTC-USD", "2020-01-01", sleep=waits.append)
    assert len(calls) == 3 and waits == [2.0, 4.0]
    assert not raw.empty
