import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def indicator_batch(months: int = 60) -> pd.DataFrame:
    """A plausible batch: every indicator, monthly, within its range."""
    days = [date(2019, 1, 1) + timedelta(days=31 * i) for i in range(months)]
    rows = []
    for d in days:
        rows += [(d, "IPCA - Monthly (%)", 0.4), (d, "Unemployment Rate (%)", 9.5),
                 (d, "USD/BRL Exchange Rate (Purchase)", 5.1)]
    return pd.DataFrame(rows, columns=["date", "indicator_name", "value"])


def bitcoin_batch(days: int = 400) -> pd.DataFrame:
    dates = [date(2023, 1, 1) + timedelta(days=i) for i in range(days)]
    return pd.DataFrame({"date": dates, "close_price": [30000.0 + i for i in range(days)],
                         "volume": [1e9] * days})


@pytest.fixture
def engine():
    """A real PostgreSQL engine (the CI service, or DB_* locally); skipped without DB_PASSWORD."""
    if not os.getenv("DB_PASSWORD"):
        pytest.skip("needs PostgreSQL: set DB_PASSWORD (and DB_HOST/DB_PORT) to run")
    from sqlalchemy import text

    import database_init
    from analytics_models.gold import engine_from_env

    eng = engine_from_env()
    with eng.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS gold_economic_indicators, gold_bitcoin_metrics"))
    database_init.initialize_database(eng)
    yield eng
    eng.dispose()
