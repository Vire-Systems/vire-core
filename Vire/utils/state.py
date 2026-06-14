import os
from pathlib import Path


redis_url = "redis://127.0.0.1:6379" #TODO : Change this URL later

logfile = os.path.abspath(os.path.join(Path.home(),"vire_logs","core", "core.log"))
os.makedirs(os.path.dirname(logfile), exist_ok=True)