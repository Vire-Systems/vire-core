import os
from pathlib import Path

job_uuid = None
remote = None
user_uuid = None
redis_url = "redis://127.0.0.1:6379" #TODO: change this to whatever the url has to be in prod
framework, package_manager = None, None

framework_images: dict = {
    "next":"vire_node-npm:v1",
    "vite":"",
    "":"",
    "static":"",
}
logfile_dir = os.path.abspath(os.path.join(Path.home(),"vire_logs/workers"))
os.makedirs(logfile_dir, exist_ok=True)
CONTAINER_EXPIRY = 300
