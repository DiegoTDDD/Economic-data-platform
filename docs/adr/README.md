# Architecture decision records

| # | Decision | Status |
|---|---|---|
| [0001](0001-postgres-gold-layer.md) | PostgreSQL as the Gold layer, created idempotently with unique keys | Accepted |
| [0002](0002-validate-then-replace-atomically.md) | Validate every batch, then replace Gold in one transaction | Accepted, replaces truncate-then-insert in two transactions |
| [0003](0003-retries-at-two-levels.md) | Retries at two levels: each HTTP call, and each pipeline step | Accepted |
| [0004](0004-one-source-down-keeps-its-history.md) | A source that fails keeps its previous rows | Accepted |
| [0005](0005-public-dashboard-from-a-ci-snapshot.md) | The public dashboard reads a snapshot refreshed by CI | Accepted |
