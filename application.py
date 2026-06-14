import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from BuildScheduler.Scheduler.db.models import init_db
from BuildScheduler.Scheduler.scheduler_loop import scheduler_loop
from Vire.utils.logger import vire_logger
from Vire.api.routers import testrouter, build_req


@asynccontextmanager
async def lifespan(app:FastAPI):
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
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(lifespan=lifespan)

app.include_router(testrouter.router)
app.include_router(build_req.router)

@app.get("/api")
async def api_status():
    return {"status":"online"}