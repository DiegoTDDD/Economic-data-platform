"""The Gold refresh against a real PostgreSQL (the CI service). Skipped without DB_PASSWORD."""

from datetime import date

import pandas as pd
import pytest
from conftest import bitcoin_batch, indicator_batch
from sqlalchemy import text

from analytics_models.gold import QualityError, replace_table
from analytics_models.quality import check_bitcoin, check_indicators

TODAY = date(2026, 11, 18)


def count(engine, sql):
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar()


def test_a_good_batch_replaces_the_table(engine):
    batch = bitcoin_batch()
    replace_table(engine, "gold_bitcoin_metrics", batch, check_bitcoin(batch, TODAY))
    replace_table(engine, "gold_bitcoin_metrics", batch, check_bitcoin(batch, TODAY))
    assert count(engine, "SELECT COUNT(*) FROM gold_bitcoin_metrics") == len(batch)


def test_a_rejected_batch_leaves_gold_unchanged(engine):
    good = bitcoin_batch()
    replace_table(engine, "gold_bitcoin_metrics", good, check_bitcoin(good, TODAY))
    bad = good.copy()
    bad.loc[0, "close_price"] = -1
    with pytest.raises(QualityError):
        replace_table(engine, "gold_bitcoin_metrics", bad, check_bitcoin(bad, TODAY))
    assert count(engine, "SELECT MIN(close_price) FROM gold_bitcoin_metrics") > 0


def test_a_failed_insert_rolls_back_the_truncate(engine):
    good = bitcoin_batch()
    replace_table(engine, "gold_bitcoin_metrics", good, check_bitcoin(good, TODAY))
    duplicated = pd.concat([good, good.head(1)], ignore_index=True)  # breaks the unique index
    report = check_bitcoin(good, TODAY)  # pretend the checks missed it
    with pytest.raises(Exception, match="(?i)unique|duplicate"):
        replace_table(engine, "gold_bitcoin_metrics", duplicated, report)
    assert count(engine, "SELECT COUNT(*) FROM gold_bitcoin_metrics") == len(good)


def test_a_missing_source_keeps_its_history(engine):
    full = indicator_batch()
    replace_table(engine, "gold_economic_indicators", full, check_indicators(full, TODAY),
                  partition_by="indicator_name")
    without_unemployment = full[full["indicator_name"] != "Unemployment Rate (%)"].copy()
    without_unemployment["value"] = without_unemployment["value"] + 0.1
    replace_table(engine, "gold_economic_indicators", without_unemployment,
                  check_indicators(without_unemployment, TODAY), partition_by="indicator_name")
    kept = count(engine, "SELECT COUNT(*) FROM gold_economic_indicators "
                         "WHERE indicator_name = 'Unemployment Rate (%)'")
    assert kept == 60
    assert count(engine, "SELECT COUNT(*) FROM gold_economic_indicators") == len(full)
