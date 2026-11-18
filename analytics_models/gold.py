"""The Gold layer in PostgreSQL: connection and the atomic, validated table refresh."""

from __future__ import annotations

import logging
import os

import pandas as pd
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL

from analytics_models.quality import QualityReport

log = logging.getLogger(__name__)


class QualityError(RuntimeError):
    """A batch failed its quality checks; the Gold table was left unchanged."""


def engine_from_env() -> Engine:
    """Engine for the Gold database from DB_* environment variables (DB_PASSWORD is required)."""
    # URL.create escapes special characters in the password (@ : / # % ...)
    return create_engine(URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER", "admin"),
        password=os.environ["DB_PASSWORD"],
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "economics_gold"),
    ))


def replace_table(engine: Engine, table: str, df: pd.DataFrame, report: QualityReport,
                  partition_by: str | None = None) -> int:
    """Replace Gold rows with `df` in one transaction, only if `report` passed.

    Without `partition_by` the whole table is replaced. With it, only the rows whose
    `partition_by` value appears in `df` are replaced, so an indicator whose source
    was down this run keeps its previous history.

    The delete and the insert run in the same transaction: if the insert fails,
    PostgreSQL rolls the delete back too, so readers never see an empty or
    half-written table.
    """
    for warning in report.warnings:
        log.warning("[%s] %s", table, warning)
    if not report.passed:
        raise QualityError(f"{table}: batch rejected, Gold unchanged: {'; '.join(report.problems)}")
    with engine.begin() as conn:
        if partition_by is None:
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY"))
        else:
            keys = sorted(df[partition_by].unique().tolist())
            conn.execute(text(f"DELETE FROM {table} WHERE {partition_by} = ANY(:keys)"),
                         {"keys": keys})
        df.to_sql(table, conn, if_exists="append", index=False)
    log.info("[%s] replaced with %s rows", table, f"{len(df):,}")
    return len(df)
