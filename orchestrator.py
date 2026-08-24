import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pipeline_steps = [
    ("Database Initialization", "database_init.py"),
    ("Bitcoin Data Ingestion", "analytics_models/bitcoin_ingestion.py"),
    ("Macroeconomic Data Ingestion", "analytics_models/macro_ingestion.py")
]

def run_pipeline():
    logging.info("Starting complete data platform orchestration...")
    for step_name, script in pipeline_steps:
        logging.info(f"[{step_name}] Running script: {script}")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if result.returncode != 0:
            err_msg = f"Error in [{step_name}] ({script}):\n{result.stderr}"
            logging.error(err_msg)
            sys.exit(1)
        else:
            out_msg = f"Success in [{step_name}]:\n{result.stdout}"
            logging.info(out_msg)
    logging.info("Pipeline executed successfully from end to end.")

if __name__ == "__main__":
    run_pipeline()
