from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.routers.health_check_route import health_check_router
from app.routers.user_routes import user_router
from app.routers.company_routes import company_router
from app.routers.quiz_routes import quiz_router
from app.core.config import Settings
from app.scheduler.apscheduler import check_quiz_completion
from fastapi.middleware.cors import CORSMiddleware

settings = Settings()

app = FastAPI(debug=settings.debug)

app.include_router(health_check_router,tags=["Health Check"])
app.include_router(user_router,tags=["User"])
app.include_router(company_router,tags=["Company"])
app.include_router(quiz_router,tags=["Quizzes"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host,
                port=settings.port, reload=settings.debug)
    
scheduler = BackgroundScheduler()
scheduler.add_job(check_quiz_completion, 'interval', days=1, start_date='2022-01-01 00:00:00')
scheduler.start()
