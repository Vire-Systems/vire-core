import os
from pathlib import Path
from dotenv import load_dotenv

import docker
import redis

load_dotenv("/home/vire/vire/.env")

# State
job_uuid = None
remote = None
user_uuid = None

install_req = False
COMMIT_ID: str | None = None

framework = None
package_manager = None
repo_name: str | None = None
OUTPUT_DIR: str | None = None

CONTAINER_EXPIRY = 300
client = docker.from_env()

# Redis
redis_url = os.getenv("REDIS_URL")

if redis_url:
    redis_con = redis.Redis.from_url(redis_url)
else:
    print(f"Redis URL in {Path(__file__).resolve()} is {redis_url}.")

# Files
logfile_dir = os.getenv("WORKER_LOGDIR")
db_file = os.getenv("DB_PATH")
if not db_file:
    print(f"'db_file' in {Path(__file__).resolve()} is {db_file}.")
    exit(1)

if logfile_dir:
    os.makedirs(logfile_dir, exist_ok=True)
else:
    print(f"'logfile_dir' in {Path(__file__).resolve()} is {logfile_dir}.")

