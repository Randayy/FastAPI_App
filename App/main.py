from fastapi import FastAPI
from app.routes.routes import router
from app.settings import HOST, PORT

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)