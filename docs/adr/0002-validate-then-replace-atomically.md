# 0002. Validate every batch, then replace Gold in one transaction

**Status:** Accepted. Before this, each ingestion ran `TRUNCATE` in one transaction and the insert in another, with no checks.

## Context
With the delete and the insert in separate transactions, a failed insert (a network drop, a type error, a constraint) left the Gold table empty. The dashboard then showed nothing until the next successful run. Nothing checked the data either: a unit change at the source, such as a rate in basis points, would have gone straight to the dashboard.

## Decision
- `analytics_models/quality.py` checks every batch: a minimum row count, no nulls, no duplicate keys, no future dates, known indicator names, and a plausible range per indicator (IPCA between -5% and 10% a month, unemployment 0 to 40%, USD/BRL 0.5 to 20, positive BTC prices).
- `replace_table` refuses a batch that failed (`QualityError`) and leaves Gold as it was.
- The delete and the insert run in the same transaction, so PostgreSQL rolls back both if either fails.

## Consequences
- Readers always see either the previous complete table or the new complete one.
- Tests run against a real PostgreSQL (the CI service): a rejected batch leaves Gold unchanged, and a failing insert (a duplicate key) rolls back the delete.
- Ranges are wide on purpose. They catch unit mistakes and corrupt rows, not unusual months.
