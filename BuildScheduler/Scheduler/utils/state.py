import os
import asyncio
import docker
from dotenv import load_dotenv

CONTAINER_REMOVAL_DELAY = 300

load_dotenv("/home/vire/vire/.env")


redis_url =  os.getenv("REDIS_URL")
sqlite_db_path = os.getenv("DB_PATH")
DB_URL = os.getenv("DB_URL")

# Worker launching stuff
python_bin_path = os.getenv("PYTHON_BIN_PATH")
worker_path = os.getenv("WORKER_PATH")

# State
docker_client = docker.from_env()
removal_tasks: set[asyncio.Task[None]] = set()
MAX_BUILDS_NUMBER = 10
