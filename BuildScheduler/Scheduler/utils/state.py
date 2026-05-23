import os, asyncio, docker

CONTAINER_REMOVAL_DELAY = 300

redis_url = "redis://127.0.0.1:6379" #TODO : Change this URL later
logfile_location = os.path.abspath(os.path.join("/home/vire/Vire-Core/worker.log")) #TODO: Change this

docker_client = docker.from_env()
removal_tasks:set[asyncio.Task] = set()