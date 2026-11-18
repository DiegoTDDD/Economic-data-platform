# 0001. PostgreSQL as the Gold layer, created idempotently with unique keys

**Status:** Accepted

## Context
The dashboard needs clean, typed time series that several processes read while the pipeline writes them. The data is small (a few thousand rows), but correctness and concurrent reads matter.

## Decision
PostgreSQL 15 in Docker. `database_init.py` creates the two Gold tables with typed, NOT NULL columns, plus unique indexes on `(date, indicator_name)` and `(date)`. It can run any number of times.

## Alternatives considered
- **DuckDB or SQLite files.** Simpler, but they have weaker concurrent access between the pipeline and the dashboard containers, and Postgres is what the stack is meant to show.
- **Let pandas create the tables (`if_exists='replace'`).** No constraints, and the types are whatever pandas infers.

## Consequences
- A duplicate day is rejected by the database itself, even if a bug slipped past the quality checks.
- One service to run, which Docker Compose handles with a health check.
