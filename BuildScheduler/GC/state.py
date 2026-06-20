import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/vire/vire/.env")

filter_labels: dict[str, str | list[str] | bool] | None = {"label":"managed_by=build_scheduler"}
logfile_dir = os.getenv("GC_LOGDIR")
redis_url = os.getenv("REDIS_URL")
db_path = os.getenv("DB_PATH")

if not logfile_dir:
    print(f"'logfile_dir in {Path(__file__).resolve()} is {logfile_dir}.")
assert logfile_dir is not None

os.makedirs(logfile_dir, exist_ok=True)

# Logging
logging_values: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn" : logging.WARN,
    "error": logging.ERROR,
    "critical" : logging.CRITICAL
}

log_level: str | None = os.getenv("LOG_LEVEL")
if not log_level:
    print(f"log level in {Path(__file__).resolve()} is 'None'")

assert log_level is not None
log_value = logging_values[log_level.lower()]