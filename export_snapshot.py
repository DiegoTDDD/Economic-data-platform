"""Export the Gold tables to Parquet for the public dashboard (data/gold_snapshot/).

Streamlit Community Cloud has no PostgreSQL, so the deployed dashboard reads this
committed snapshot. The refresh-snapshot workflow runs the pipeline and this script
every month and commits the result.

Usage (with the database up and DB_* set):
    python export_snapshot.py
"""

import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from analytics_models.gold import engine_from_env  # noqa: E402

log = logging.getLogger(__name__)
SNAPSHOT_DIR = ROOT / "data" / "gold_snapshot"
TABLES = {
    "gold_bitcoin_metrics": (
        "SELECT date, close_price, volume FROM gold_bitcoin_metrics ORDER BY date"
    ),
    "gold_economic_indicators": (
        "SELECT date, indicator_name, value FROM gold_economic_indicators "
        "ORDER BY indicator_name, date"
    ),
}


def export(snapshot_dir: Path = SNAPSHOT_DIR) -> dict[str, int]:
    engine = engine_from_env()
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, query in TABLES.items():
        df = pd.read_sql(query, engine)
        df.to_parquet(snapshot_dir / f"{name}.parquet", index=False)
        counts[name] = len(df)
        log.info("%s: %s rows", name, f"{len(df):,}")
    return counts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    export()
