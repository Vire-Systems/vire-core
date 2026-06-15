import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/vire/vire/.env")

filter_labels: dict[str, str | list[str] | bool] | None = {"label":"managed_by=build_scheduler"}

logfile_dir = os.getenv("GC_LOGDIR")
if logfile_dir:
    os.makedirs(logfile_dir, exist_ok=True)
else:
    print(f"'logfile_dir in {Path(__file__).resolve()} is {logfile_dir}.")