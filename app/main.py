from fastapi import FastAPI
from .routers.health_check_route import router
from .core.config import settings


app = FastAPI(debug=settings.debug)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port,reload=settings.debug)

