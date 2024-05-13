from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db.connect_postgresql import get_session
from app.db.user_models import Quiz, User, Notification , Result, Company
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

async def check_quiz_completion(db:AsyncSession = Depends(get_session)):
    logging.info("Running check_quiz_completion")
    users = await db.execute(select(User))
    users = users.scalars().all()

    companies = await db.execute(select(Company))
    companies = companies.scalars().all()

    for user in users:
        company = await db.execute(select(Company).join(User).where(User.id == user.id))
        company = company.scalars().first()

        if company:
            quizzes = await db.execute(select(Quiz).where(Quiz.company_id == company.id))
            quizzes = quizzes.scalars().all()
            notifications = []
            for quiz in quizzes:
                last_taken = await db.execute(select(Result).where(Result.user_id == user.id, Result.quiz_id == quiz.id).order_by(Result.created_at.desc()))
                last_taken = last_taken.scalars().first()
                if last_taken and last_taken.created_at < datetime.now() - timedelta(days=1):
                    notification = Notification(text=f"You have not taken the quiz '{quiz.title}' in the last 1 days. Please take the quiz.", user_id=user.id)
                    notifications.append(notification)
            await db.add_all(notifications)
            await db.commit()
