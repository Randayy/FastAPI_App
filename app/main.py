from fastapi import FastAPI

from app.routers.health_check_route import router
from app.routers.user_routes import user_router
from app.core.config import Settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

settings = Settings()

app = FastAPI(debug=settings.debug)
add_pagination(app)

app.include_router(router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"] 
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",host=settings.host, port=settings.port,reload=settings.debug)



