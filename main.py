import uvicorn, logging, os
from application import app
from BuildScheduler.Scheduler.utils.state import logfile_dir
from BuildScheduler.shared.logger_setup import setup_async_logging, stop_async_logging

logger = logging.getLogger(__name__)

#TODO: Move logging to application.py

if __name__=="__main__":
    try:
        logfile_location = os.path.join(logfile_dir, "scheduler.log")
        setup_async_logging(logfile_location)
        uvicorn.run("main:app", host="127.0.0.1", port = 8000)
    finally:
        stop_async_logging()