from fastapi import FastAPI

from app.routers.health_check_route import router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(debug=settings.debug)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port,reload=settings.debug)

