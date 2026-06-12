import os, asyncio, docker
from pathlib import Path

CONTAINER_REMOVAL_DELAY = 300

redis_url = "redis://127.0.0.1:6379" #TODO : Change this URL later

logfile_dir = os.path.abspath(os.path.join(Path.home(),"vire_logs","core"))
os.makedirs(logfile_dir, exist_ok=True)
docker_client = docker.from_env()
removal_tasks: set[asyncio.Task[None]] = set()


sqlite_db_path = os.path.join(Path.home(), "Vire-DB", "vire_state.db")

MAX_BUILDS_NUMBER = 10
worker_task_set: set[asyncio.Task[None]] = set()