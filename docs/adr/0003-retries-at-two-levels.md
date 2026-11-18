# 0003. Retries at two levels: each HTTP call, and each pipeline step

**Status:** Accepted

## Context
The BCB API answers 429 and 5xx under load, and Yahoo Finance often rate-limits or returns empty frames. On a cold start the database may still be coming up when the first step runs.

## Decision
- **Per call** (`sources.with_retries`, `download_yfinance`): up to 4 attempts with exponential backoff (2, 4 and 8 seconds), only for timeouts, connection errors and 429/5xx. Any other 4xx is a bug on our side and fails immediately.
- **Per step** (`orchestrator.run_step`): each script gets 3 attempts, 15 seconds apart. A step that fails every attempt stops the pipeline with exit code 1, so later steps never run on a half-loaded state.
- The sleep function is injected, so tests check the exact waits without waiting.

## Consequences
- Brief outages recover by themselves, and real failures still surface quickly and loudly.
- In the worst case a dead source costs about 14 seconds per call, times 3 step attempts.
