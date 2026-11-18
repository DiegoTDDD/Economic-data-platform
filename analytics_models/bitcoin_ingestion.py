"""Ingest daily BTC-USD prices (yfinance) into gold_bitcoin_metrics."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics_models.gold import engine_from_env, replace_table  # noqa: E402
from analytics_models.quality import check_bitcoin  # noqa: E402
from analytics_models.sources import download_yfinance, parse_bitcoin  # noqa: E402

log = logging.getLogger(__name__)
START = "2020-01-01"


def ingest_bitcoin_data() -> int:
    log.info("Downloading BTC-USD daily history since %s ...", START)
    df = parse_bitcoin(download_yfinance("BTC-USD", start=START))
    return replace_table(engine_from_env(), "gold_bitcoin_metrics", df, check_bitcoin(df))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ingest_bitcoin_data()
