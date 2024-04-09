from fastapi import FastAPI
from . import *
from routers.routes import router


app = FastAPI()

app.include_router(router)

