import asyncio
from collections import defaultdict

db_build_queue = asyncio.Queue()
scheduler_lock = asyncio.Lock()
queue_insert_lock = asyncio.Lock()
job_status_locks = defaultdict(asyncio.Lock)