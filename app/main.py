from fastapi import FastAPI
from .routers.health_check_route import router
from .core.config import Settings
from fastapi.middleware.cors import CORSMiddleware

settings = Settings()

app = FastAPI(debug=settings.debug)

app.include_router(router)


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



