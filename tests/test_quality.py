"""The checks that decide whether a batch may replace a Gold table."""

from datetime import date

import pandas as pd
from conftest import bitcoin_batch, indicator_batch

from analytics_models.quality import check_bitcoin, check_indicators

TODAY = date(2026, 11, 18)


def test_a_plausible_batch_passes():
    report = check_indicators(indicator_batch(), TODAY)
    assert report.passed and not report.warnings
    assert check_bitcoin(bitcoin_batch(), TODAY).passed


def test_values_outside_their_range_are_rejected():
    batch = indicator_batch()
    batch.loc[batch["indicator_name"] == "IPCA - Monthly (%)", "value"] = 42.0
    report = check_indicators(batch, TODAY)
    assert not report.passed
    assert any("IPCA" in p and "outside" in p for p in report.problems)


def test_duplicates_nulls_and_future_dates_are_rejected():
    batch = indicator_batch()
    batch = pd.concat([batch, batch.head(1)], ignore_index=True)
    batch.loc[5, "value"] = None
    batch.loc[6, "date"] = date(2030, 1, 1)
    problems = " | ".join(check_indicators(batch, TODAY).problems)
    assert "duplicate" in problems and "nulls" in problems and "future" in problems


def test_a_missing_source_is_a_warning_not_a_rejection():
    batch = indicator_batch()
    batch = batch[batch["indicator_name"] != "Unemployment Rate (%)"]
    report = check_indicators(batch, TODAY)
    assert report.passed
    assert report.warnings == ["Unemployment Rate (%): no rows in this batch"]


def test_unknown_indicators_and_tiny_batches_are_rejected():
    batch = pd.concat([indicator_batch(), pd.DataFrame(
        [{"date": date(2024, 1, 1), "indicator_name": "Selic", "value": 10.5}])])
    assert any("unknown" in p for p in check_indicators(batch, TODAY).problems)
    assert any("only" in p for p in check_indicators(indicator_batch(3), TODAY).problems)


def test_bitcoin_prices_must_be_positive():
    batch = bitcoin_batch()
    batch.loc[10, "close_price"] = 0
    batch.loc[11, "volume"] = -1
    problems = check_bitcoin(batch, TODAY).problems
    assert "non-positive close prices" in problems and "negative volume" in problems
