# 0005. The public dashboard reads a snapshot refreshed by CI

**Status:** Accepted

## Context
Streamlit Community Cloud has no PostgreSQL and should not call the sources on every visit.

## Decision
`export_snapshot.py` writes both Gold tables to `data/gold_snapshot/`. The `refresh-snapshot` workflow runs the real pipeline every month on a fresh PostgreSQL service in CI: sources, checks, Gold, export. It checks that the dashboard renders, and commits the snapshot only if all of that passed. The dashboard reads PostgreSQL when `DB_PASSWORD` is set (Docker Compose) and the snapshot otherwise.

## Consequences
- A free, always-on public dashboard, at most a month old, with its date shown on the page.
- Each monthly run also tests the whole pipeline against the live sources.
