import os


job_uuid = None
remote = None
user_uuid = None
redis_url = "redis://127.0.0.1:6379" #TODO: change this to whatever the url has to be in prod
framework, package_manager = None, None

framework_images: dict = {
    "next":"node-20",
    "vite":"",
    "":"",
    "static":"",
}
logfile_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "worker.log"))
