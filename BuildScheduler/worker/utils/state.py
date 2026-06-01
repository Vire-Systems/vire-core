import os, docker, redis
from pathlib import Path

job_uuid = None
remote = None
user_uuid = None

install_req = False
framework, package_manager = None, None
repo_name = None
OUTPUT_DIR = None

redis_url = "redis://127.0.0.1:6379" #TODO: change this to whatever the url has to be in prod
redis_con = redis.Redis.from_url(redis_url)

logfile_dir = os.path.abspath(os.path.join(Path.home(),"vire_logs/workers"))
os.makedirs(logfile_dir, exist_ok=True)
CONTAINER_EXPIRY = 300

client = docker.from_env()