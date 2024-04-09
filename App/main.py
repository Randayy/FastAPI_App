from fastapi import FastAPI
from .routers.routes import router
from .settings import HOST, PORT

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)