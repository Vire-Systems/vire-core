import uvicorn, logging, os
from application import app
from Vire.utils.state import logfile
from BuildScheduler.shared.logger_setup import setup_async_logging, stop_async_logging

logger = logging.getLogger(__name__)

#TODO: Move logging to application.py

if __name__=="__main__":
    try:
        setup_async_logging(logfile)
        uvicorn.run("main:app", host="127.0.0.1", port = 8000)
    finally:
        stop_async_logging()
