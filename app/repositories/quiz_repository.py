from app.db.user_models import User, Quiz, Company, Question, Answer, CompanyMember
from app.schemas.quiz_shemas import QuizResponseSchema, QuizSchema, QuestionSchema, AnswerSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.user_models import User, Role, Result, UserAnswer
from fastapi import HTTPException
from sqlalchemy import select
import logging
from sqlalchemy.exc import DBAPIError
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from datetime import datetime


class QuizRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_quiz_by_id(self, quiz_id: UUID) -> Quiz:
        stmt = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.db.execute(stmt)
        quiz = result.scalars().first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        quiz_dict = quiz.__dict__
        return quiz_dict

    async def get_quiz_questions(self, quiz_id: UUID):
        stmt = select(Question).where(Question.quiz_id ==
                                      quiz_id).options(joinedload(Question.answers))
        result = await self.db.execute(stmt)
        questions = result.scalars().unique().all()
        questions_dict = [question.__dict__ for question in questions]
        return questions_dict

    async def get_quiz_questions_ids(self, quiz_id: UUID) -> List[UUID]:
        stmt = select(Question).where(Question.quiz_id ==
                                      quiz_id).options(joinedload(Question.answers))
        result = await self.db.execute(stmt)
        questions = result.scalars().unique().all()
        question_ids = []
        for question in questions:
            question_ids.append(question.id)

        return question_ids

    async def get_question_answers(self, question_id: UUID):
        stmt = select(Answer).where(Answer.question_id == question_id)
        result = await self.db.execute(stmt)
        answers = result.scalars().unique().all()
        answers_dict = [answer.__dict__ for answer in answers]
        return answers_dict

    async def get_question_answers_ids(self, question_id: UUID):
        stmt = select(Answer).where(Answer.question_id == question_id)
        result = await self.db.execute(stmt)
        answers = result.scalars().unique().all()
        answers_ids = []
        for answer in answers:
            answers_ids.append(answer.id)

        return answers_ids

    async def check_if_user_is_owner_or_admin_in_this_quiz_company_by_quiz_id(self, current_user_id: UUID, quiz_id: UUID):
        quiz_select = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.db.execute(quiz_select)
        quiz = result.scalars().first()

        if not quiz:
            raise HTTPException(status_code=404, detail="quiz not found")

        company_member_select = select(CompanyMember).where(and_(
            CompanyMember.user_id == current_user_id, CompanyMember.company_id == quiz.company_id))
        result = await self.db.execute(company_member_select)
        company_member = result.scalars().first()
        if not company_member:
            raise HTTPException(
                status_code=403, detail='You are not member of company with this quiz, you are not permitted to see this)')

        if company_member.role != Role.ADMIN and company_member.role != Role.OWNER:
            raise HTTPException(
                status_code=403, detail='You are not owner or admin of company with this quiz, you are not permitted to see this)')

    async def check_if_user_is_owner_or_admin_in_this_quiz_company(self, current_user_id: UUID, question_id: UUID):
        question_select = select(Question).where(Question.id == question_id)
        result = await self.db.execute(question_select)
        question = result.scalars().first()
        if not question:
            raise HTTPException(status_code=404, detail="question not found")

        quiz = question.quiz
        if not quiz:
            raise HTTPException(status_code=404, detail="quiz not found")
        company_member_select = select(CompanyMember).where(and_(
            CompanyMember.user_id == current_user_id, CompanyMember.company_id == quiz.company_id))
        result = await self.db.execute(company_member_select)
        company_member = result.scalars().first()
        if not company_member:
            raise HTTPException(
                status_code=403, detail='You are not member of company with this quiz question, you are not permitted to see this)')

        if company_member.role != Role.ADMIN and company_member.role != Role.OWNER:
            raise HTTPException(
                status_code=403, detail='You are not owner or admin of company with this quiz question, you are not permitted to see this)')

    async def create_quiz(self, quiz_data: dict, company_id: UUID):
        new_quiz = Quiz(
            title=quiz_data['title'],
            description=quiz_data.get('description'),
            frequency_days=quiz_data['frequency_days'],
            company_id=company_id
        )
        self.db.add(new_quiz)
        questions = []
        answers = []
        for question_data in quiz_data['questions']:
            question = Question(
                question_text=question_data['question_text'],
                quiz=new_quiz
            )
            questions.append(question)

            for answer_data in question_data['answers']:
                answer = Answer(
                    answer_text=answer_data['answer_text'],
                    is_correct=answer_data['is_correct'],
                    question=question
                )
                answers.append(answer)

        self.db.add_all(questions)
        self.db.add_all(answers)
        await self.db.commit()
        await self.db.refresh(new_quiz)
        quiz_dict = new_quiz.__dict__
        return quiz_dict

    async def check_if_user_is_admin_or_owner_in_company(self, current_user_id: UUID, company_id: UUID):
        company_member = await self.db.execute(select(CompanyMember).where(CompanyMember.company_id == company_id).where(CompanyMember.user_id == current_user_id))
        company_member = company_member.scalars().first()
        if not company_member:
            raise HTTPException(
                status_code=403, detail="You are not a member of this company")
        if company_member.role != Role.ADMIN and company_member.role != Role.OWNER:
            raise HTTPException(
                status_code=403, detail="You are not an admin or owner in this company")
        return company_member

    async def delete_quiz(self, quiz_id: UUID):
        quiz_select = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.db.execute(quiz_select)
        quiz = result.scalars().first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        await self.db.delete(quiz)
        await self.db.commit()
        return "Quiz deleted"

    async def update_quiz(self, quiz_id: UUID, quiz_data: dict):
        quiz_select = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.db.execute(quiz_select)
        quiz = result.scalars().first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        quiz.title = quiz_data['title']
        quiz.description = quiz_data.get('description')
        quiz.frequency_days = quiz_data['frequency_days']
        for question_data in quiz_data['questions']:
            question_id = question_data.get('id')

            if question_id:
                question_select = select(Question).where(
                    Question.id == question_id)
                question_result = await self.db.execute(question_select)
                question = question_result.scalars().first()
                if not question:
                    raise HTTPException(
                        status_code=404, detail=f"Question with id {question_id} not found")
                question.question_text = question_data['question_text']

            else:
                question = Question(
                    question_text=question_data['question_text'], quiz=quiz)

                self.db.add(question)

            for answer_data in question_data['answers']:
                answer_id = answer_data.get('id')
                if answer_id:
                    answer_select = select(Answer).where(
                        Answer.id == answer_id)
                    answer_result = await self.db.execute(answer_select)
                    answer = answer_result.scalars().first()
                    if not answer:
                        raise HTTPException(
                            status_code=404, detail=f"Answer with id {answer_id} not found")
                    answer.answer_text = answer_data['answer_text']
                    answer.is_correct = answer_data['is_correct']
                else:
                    answer = Answer(
                        answer_text=answer_data['answer_text'], is_correct=answer_data['is_correct'], question=question)
                    self.db.add(answer)

        await self.db.commit()
        await self.db.refresh(quiz)
        quiz_dict = quiz.__dict__
        return quiz_dict

    async def list_quizzes(self, company_id: UUID, page: int, limit: int):
        quizzes = await self.db.execute(select(Quiz).where(Quiz.company_id == company_id).offset((page - 1) * limit).limit(limit))
        quizzes = quizzes.scalars().all()
        quizzes_dict = [quiz.__dict__ for quiz in quizzes]
        return quizzes_dict

    async def check_if_user_member_of_company(self, current_user_id: UUID, company_id: UUID):
        company_member = await self.db.execute(select(CompanyMember).where(CompanyMember.company_id == company_id).where(CompanyMember.user_id == current_user_id))
        company_member = company_member.scalars().first()
        if not company_member:
            raise HTTPException(
                status_code=403, detail="You are not a member of this company")

# be-12
    async def check_if_user_alredy_submitted_quiz(self, current_user_id: UUID, quiz_id: UUID):
        result = await self.db.execute(select(Result).where(Result.quiz_id == quiz_id).where(Result.user_id == current_user_id))
        result = result.scalars().first()
        return result

    async def submit_quiz_answers(self, user_answers: dict, current_user_id: UUID, quiz_id: UUID):
        result = await self.db.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = result.scalars().first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        questions = await self.db.execute(select(Question).where(Question.quiz_id == quiz_id))
        questions = questions.scalars().all()
        if not questions:
            raise HTTPException(status_code=404, detail="Questions not found")
        question_ids = [question.id for question in questions]
        questions_answers_dict = []
        for question_id in question_ids:
            question_answers = await self.get_question_answers(question_id)
            questions_answers_dict.append(question_answers)
        user_answers = user_answers['questions_answers']
        user_answers_list_ids = [ans['answer_id']
                                 for answer in user_answers for ans in answer['answers']]
        correct_answers = 0
        questions = 0
        for question_answers in questions_answers_dict:
            for question_answer in question_answers:
                if question_answer['is_correct'] == True and question_answer['id'] in user_answers_list_ids:
                    correct_answers += 1
            questions += 1

        score = correct_answers/questions
        quiz_result = Result(
            quiz_id=quiz_id,
            user_id=current_user_id,
            score=score,
            created_at=datetime.utcnow()
        )

        self.db.add(quiz_result)
        await self.db.commit()
        await self.db.refresh(quiz_result)

        for answer in user_answers:
            question_id = answer['question_id']
            answers = []
            for ans in answer['answers']:
                user_answer = UserAnswer(
                    result_id=quiz_result.id,
                    question_id=question_id,
                    answer_id=ans['answer_id']
                )
                answers.append(user_answer)
            self.db.add_all(answers)

        await self.db.commit()

        return {"message": "Quiz submitted successfully", "score": score}

    async def get_quiz_results_for_user(self, quiz_id: UUID, current_user_id: UUID):
        user_result = await self.db.execute(select(Result).where(Result.quiz_id == quiz_id).where(Result.user_id == current_user_id))
        user_result = user_result.scalars().first()
        if not user_result:
            raise HTTPException(
                status_code=404, detail="You have not submitted this quiz yet")
        return user_result

    async def get_user_avarage_mark_from_quizzes(self, user_id: UUID) -> float:
        results = await self.db.execute(select(Result).where(Result.user_id == user_id))
        results = results.scalars().all()
        if not results:
            raise HTTPException(
                status_code=404, detail="You have not submitted any quiz yet")

        sum_of_scores = 0
        quizzes = 0
        for result in results:
            sum_of_scores += result.score
            quizzes += 1

        avarage_mark = sum_of_scores/quizzes
        return avarage_mark

    async def get_user_avarage_mark_from_quizzes_in_company(self, company_id: UUID, user_id: UUID):
        results = await self.db.execute(select(Result).join(Quiz).where(Quiz.company_id == company_id).where(Result.user_id == user_id))
        results = results.scalars().all()
        if not results:
            raise HTTPException(
                status_code=404, detail="You have not submitted any quiz in this company yet")

        sum_of_scores = 0
        quizzes = 0
        for result in results:
            sum_of_scores += result.score
            quizzes += 1

        avarage_mark = sum_of_scores/quizzes
        return avarage_mark
