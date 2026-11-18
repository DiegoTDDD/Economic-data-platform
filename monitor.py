"""Quick health check: running containers and a connection to the Gold database."""

import logging
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analytics_models.gold import engine_from_env  # noqa: E402

log = logging.getLogger(__name__)


def check_infrastructure() -> bool:
    log.info("=== PLATFORM HEALTH MONITOR ===")
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}} - {{.Status}}"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        log.info("Containers:\n%s", result.stdout or "none running")
    else:
        log.error("Could not query Docker: %s", result.stderr.strip())
    try:
        with engine_from_env().connect() as conn:
            rows = conn.execute(text(
                "SELECT (SELECT COUNT(*) FROM gold_economic_indicators), "
                "(SELECT COUNT(*) FROM gold_bitcoin_metrics)"
            )).one()
        log.info("PostgreSQL Gold layer responding: %s indicator rows, %s bitcoin rows", *rows)
        return True
    except Exception as exc:  # noqa: BLE001 - report any connection problem
        log.error("Database check failed: %s", exc)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sys.exit(0 if check_infrastructure() else 1)
