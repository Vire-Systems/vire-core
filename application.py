from fastapi import FastAPI
from Vire.api.routers import testrouter


app = FastAPI()

app.include_router(testrouter.router)