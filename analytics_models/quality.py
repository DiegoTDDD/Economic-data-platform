"""Data-quality checks run on every batch before it may replace a Gold table.

A batch that fails any check is rejected and the Gold table keeps its previous
contents (ADR 0002). Ranges are deliberately wide: they catch unit mistakes
(a rate in basis points, a price in cents) and corrupt rows, not unusual months.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

# indicator -> (lowest plausible value, highest plausible value)
INDICATOR_RANGES: dict[str, tuple[float, float]] = {
    "IPCA - Monthly (%)": (-5.0, 10.0),
    "Unemployment Rate (%)": (0.0, 40.0),
    "USD/BRL Exchange Rate (Purchase)": (0.5, 20.0),
}
MIN_ROWS = {"indicators": 50, "bitcoin": 365}


@dataclass
class QualityReport:
    table: str
    rows: int
    problems: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.problems


def _common(df: pd.DataFrame, report: QualityReport, keys: list[str], today: date) -> None:
    if report.rows < MIN_ROWS[report.table]:
        minimum = MIN_ROWS[report.table]
        report.problems.append(f"only {report.rows} rows (expected at least {minimum})")
    nulls = int(df.isna().any(axis=1).sum()) if len(df) else 0
    if nulls:
        report.problems.append(f"{nulls} rows with nulls")
    duplicates = int(df.duplicated(subset=keys).sum()) if len(df) else 0
    if duplicates:
        report.problems.append(f"{duplicates} duplicate {'/'.join(keys)} rows")
    future = int((pd.to_datetime(df["date"]) > pd.Timestamp(today)).sum()) if len(df) else 0
    if future:
        report.problems.append(f"{future} rows dated in the future")


def check_indicators(df: pd.DataFrame, today: date | None = None) -> QualityReport:
    """Macro indicators: shape, keys, dates, known names, plausible ranges, every source present."""
    today = today or date.today()
    report = QualityReport("indicators", len(df))
    _common(df, report, ["date", "indicator_name"], today)
    unknown = sorted(set(df["indicator_name"]) - set(INDICATOR_RANGES))
    if unknown:
        report.problems.append(f"unknown indicators: {unknown}")
    for name, (low, high) in INDICATOR_RANGES.items():
        values = df.loc[df["indicator_name"] == name, "value"]
        if values.empty:
            # One source down should not wipe the others: warn, keep the batch.
            report.warnings.append(f"{name}: no rows in this batch")
            continue
        out = int(((values < low) | (values > high)).sum())
        if out:
            report.problems.append(f"{name}: {out} values outside [{low}, {high}]")
    return report


def check_bitcoin(df: pd.DataFrame, today: date | None = None) -> QualityReport:
    """BTC-USD: shape, keys, dates, positive prices, non-negative volume."""
    today = today or date.today()
    report = QualityReport("bitcoin", len(df))
    _common(df, report, ["date"], today)
    if len(df) and (df["close_price"] <= 0).any():
        report.problems.append("non-positive close prices")
    if len(df) and (df["volume"].fillna(0) < 0).any():
        report.problems.append("negative volume")
    return report
