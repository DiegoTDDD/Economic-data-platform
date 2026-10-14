import subprocess
import sys
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pipeline_steps = [
    ("Database Initialization", "database_init.py"),
    ("Bitcoin Data Ingestion", "analytics_models/bitcoin_ingestion.py"),
    ("Macroeconomic Data Ingestion", "analytics_models/macro_ingestion.py")
]

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 15

def run_step(step_name, script):
    """Run one pipeline step, retrying on failure (database still starting, transient API errors)."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Success in [{step_name}]:\n{result.stdout}")
            return
        logging.error(f"Error in [{step_name}] ({script}), attempt {attempt}/{MAX_ATTEMPTS}:\n{result.stderr}")
        if attempt < MAX_ATTEMPTS:
            logging.info(f"Retrying in {RETRY_DELAY_SECONDS}s...")
            time.sleep(RETRY_DELAY_SECONDS)
    sys.exit(1)

def run_pipeline():
    logging.info("Starting complete data platform orchestration...")
    for step_name, script in pipeline_steps:
        logging.info(f"[{step_name}] Running script: {script}")
        run_step(step_name, script)
    logging.info("Pipeline executed successfully from end to end.")

if __name__ == "__main__":
    run_pipeline()
