import os
from dotenv import load_dotenv

load_dotenv("/home/vire/vire/.env")

redis_url = os.getenv("REDIS_URL") #TODO : Change this URL later

logfile_dir = os.getenv("CORE_LOGDIR")

if logfile_dir:
    logfile = os.path.join(logfile_dir, "core.log")
    os.makedirs(os.path.dirname(logfile), exist_ok=True)