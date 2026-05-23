import asyncio

container_delete_lock = asyncio.Lock()
task_removal_lock = asyncio.Lock()