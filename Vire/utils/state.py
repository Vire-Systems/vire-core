import os
from pathlib import Path

logfile_dir = os.path.abspath(os.path.join(Path.home(), "vire_logs", "core"))
os.makedirs(logfile_dir, exist_ok=True)

redis_url = "redis://127.0.0.1:6379" #TODO: change this to whatever the url has to be in prod
