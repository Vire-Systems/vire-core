from fastapi import FastAPI
from Vire.api.routers import testrouter, build_req

app = FastAPI()

app.include_router(testrouter.router)
app.include_router(build_req.router)
