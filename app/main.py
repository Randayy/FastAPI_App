from fastapi import FastAPI
from .routers.routes import router


app = FastAPI()

app.include_router(router)

