"""state"""

from pathlib import Path
import os

redis_url = "redis://127.0.0.1:6379" #TODO: change this to whatever the url has to be in prod
sqlite_db_path = os.path.join(Path.home(), "Vire-DB", "vire_state.db")