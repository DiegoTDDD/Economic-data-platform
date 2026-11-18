"""Run the pipeline steps in order, retrying each one before giving up.

Retries cover what is transient at this level (the database still starting, a
source rate-limiting); the ingestion scripts also retry each HTTP call
themselves. A step that fails every attempt stops the pipeline with exit code 1.
"""

from __future__ import annotations

import logging
import subprocess
import sys
import time
from collections.abc import Callable

log = logging.getLogger(__name__)

PIPELINE_STEPS = [
    ("Database Initialization", "database_init.py"),
    ("Bitcoin Data Ingestion", "analytics_models/bitcoin_ingestion.py"),
    ("Macroeconomic Data Ingestion", "analytics_models/macro_ingestion.py"),
]
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 15

Runner = Callable[[list[str]], subprocess.CompletedProcess]


def _run(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True)


def run_step(step_name: str, script: str, runner: Runner = _run,
             sleep: Callable[[float], None] = time.sleep,
             attempts: int = MAX_ATTEMPTS, delay: float = RETRY_DELAY_SECONDS) -> int:
    """Run one step until it succeeds; return the attempt that worked or raise SystemExit(1)."""
    for attempt in range(1, attempts + 1):
        result = runner([sys.executable, script])
        if result.returncode == 0:
            log.info("[%s] succeeded (attempt %d)\n%s", step_name, attempt,
                     result.stderr or result.stdout)
            return attempt
        log.error("[%s] failed, attempt %d/%d:\n%s", step_name, attempt, attempts,
                  result.stderr or result.stdout)
        if attempt < attempts:
            log.info("Retrying in %ss...", delay)
            sleep(delay)
    raise SystemExit(1)


def run_pipeline(runner: Runner = _run, sleep: Callable[[float], None] = time.sleep) -> None:
    log.info("Starting the pipeline...")
    for step_name, script in PIPELINE_STEPS:
        run_step(step_name, script, runner=runner, sleep=sleep)
    log.info("Pipeline finished.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    run_pipeline()
