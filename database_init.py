"""Create the Gold tables (idempotent); unique indexes block duplicate days in the database."""

import logging
import sys
from pathlib import Path

from sqlalchemy import Engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analytics_models.gold import engine_from_env  # noqa: E402

log = logging.getLogger(__name__)

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS gold_economic_indicators (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        indicator_name VARCHAR(100) NOT NULL,
        value NUMERIC(18, 4) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS ux_indicators_date_name
        ON gold_economic_indicators (date, indicator_name)
    """,
    """
    CREATE TABLE IF NOT EXISTS gold_bitcoin_metrics (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        close_price NUMERIC(18, 2) NOT NULL,
        volume NUMERIC(24, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_bitcoin_date ON gold_bitcoin_metrics (date)",
]


def initialize_database(engine: Engine | None = None) -> None:
    engine = engine or engine_from_env()
    log.info("Initializing the Gold layer schema...")
    with engine.begin() as conn:
        for statement in SCHEMA:
            conn.execute(text(statement))
    log.info("Gold layer tables ready.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    initialize_database()
