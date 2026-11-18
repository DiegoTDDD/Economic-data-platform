# 0004. A source that fails keeps its previous rows

**Status:** Accepted

## Context
The macro batch combines three sources. If one is down, refusing the whole batch would also hold back the two healthy ones. Writing a partial batch with a full-table replace would instead delete the missing indicator's entire history.

## Decision
The macro table is replaced per indicator (`partition_by="indicator_name"`): only the indicators present in the batch are deleted and re-inserted. A missing indicator produces a warning and keeps its previous rows. If no source answers, nothing is written.

## Consequences
- One outage costs one indicator a refresh, not its history.
- A test checks this against PostgreSQL. The dashboard caption shows the latest observation date, so a stale indicator can be seen.
