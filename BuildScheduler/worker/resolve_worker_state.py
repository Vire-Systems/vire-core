import sqlite3
from contextlib import contextmanager
from typing import Literal
from BuildScheduler.worker.utils.vire_logger import cfn_log
from utils.state import db_file

assert db_file is not None, "SQLite database filepath cannot be empty."

status_update_allowlist: dict[str,list] = {
    "queued": ["running", "crashed", "finished", "cancelled"],
    "running": ["crashed", "finished", "cancelled"],
    "crashed" : [], "finished": [], "cancelled": []
}


@contextmanager
def db_session(db_name: str):
    connection = sqlite3.connect(db_name)
    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")

        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def fetch_job_status(job_uuid: str, user_uuid: str)-> str:
    with db_session(db_file) as conn:
        cursor = conn.cursor()
        query = """
            SELECT job_uuid FROM BuildState
            WHERE job_uuid=? AND user_uuid=?
            """
        result: str = cursor.execute(query).fetchone()
        return result

def update_job_state(
    job_uuid: str,
    status: Literal["queued", "running", "crashed", "finished", "cancelled"],
    prev_status: Literal["queued", "running", "crashed", "finished", "cancelled"]
)-> None:
    allowed_updates: list[str] = status_update_allowlist[prev_status]
    if status not in allowed_updates:
        cfn_log("warn", "'%s' cannot be updated to '%s' for Job UUID '%s'.", prev_status, status, job_uuid)

    with db_session(db_file) as conn:
        cursor = conn.cursor()
        query = """
            UPDATE BuildState
            SET status=?
            WHERE 
            job_uuid=? AND status=?
            """
        cursor.execute(query, (status, job_uuid, prev_status))