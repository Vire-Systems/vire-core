"""
The module used in main.py
This provides the fastapi app with the lifespan.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from BuildScheduler.Scheduler.db.models import init_db
from BuildScheduler.Scheduler.scheduler_loop import scheduler_loop
from BuildScheduler.shared.scheduler_logger import vire_logger
from Vire.api.routers import testrouter, build_req
from Vire.utils import async_requests


@asynccontextmanager
async def lifespan(app:FastAPI):
    """FastAPI lifespan CM"""
    print("INFO:     [Vire Core] Starting up.")
    await vire_logger("info", "[Vire core] start up.")
    tasks = []
    await init_db()
    tasks.append(asyncio.create_task(scheduler_loop()))
    try:
        yield
    finally:
        print("INFO:     [Vire Core] Shutting down.")
        await vire_logger("info", "[Vire Core] shutting down.")
        if not async_requests.client:
            print("INFO:     [async req setup] No client found. Ignoring aclose()...")
        else:
            await async_requests.client.aclose()
            print("INFO:     [async req setup] client pool closed.")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(lifespan=lifespan)

app.include_router(testrouter.router)
app.include_router(build_req.router)

@app.get("/api")
async def api_status():
    return {"status":"online"}
