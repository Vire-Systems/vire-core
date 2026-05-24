import os
from pathlib import Path
filter_labels: dict[str, str] = {"label":"managed_by=build_scheduler"}

logfile_dir = os.path.abspath(os.path.join(Path.home(),"vire_logs","gc"))
os.makedirs(logfile_dir, exist_ok=True) 