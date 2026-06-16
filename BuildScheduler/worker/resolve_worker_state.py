import sqlite3
from contextlib import contextmanager
from typing import Literal
from utils.state import db_file


status_update_allowlist: dict[str,list] = {
    "queued": ["running", "crashed", "finished", "cancelled"],
    "running": ["crashed", "finished", "cancelled"],
    "crashed" : [], "finished": [], "cancelled": []
}


@contextmanager
def db_session(db_name: str):
    connection = sqlite3.connect(db_name)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_job_state(
    job_uuid: str,
    status: Literal["queued", "running", "crashed", "finished", "cancelled"],
    prev_status: Literal["queued", "running", "crashed", "finished", "cancelled"]
)-> None:
    allowed_updates: list[str] = status_update_allowlist[prev_status]
    if status not in allowed_updates:
        print(f"{prev_status} cannot be updated to {status}.")

    assert db_file is not None
    with db_session(db_file) as conn:
        cursor = conn.cursor()
        query = """
            UPDATE BuildState
            SET status=?
            WHERE 
            job_uuid=? AND status=?
            """
        cursor.execute(query, (status, job_uuid, prev_status))