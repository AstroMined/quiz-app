# filename: /code/quiz-app/quiz-app-backend/app/api/endpoints/questions.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_questions import (create_question_in_db, 
                                     delete_question_from_db, read_question_from_db,
                                     read_questions_from_db, update_question_in_db)
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.questions import (DetailedQuestionSchema,
                                   QuestionCreateSchema, QuestionSchema,
                                   QuestionUpdateSchema,
                                   QuestionWithAnswersCreateSchema)
from app.services.logging_service import logger
from app.services.user_service import get_current_user

router = APIRouter()

@router.post("/questions/", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
def create_question_endpoint(
    question: QuestionCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    created_question = create_question_in_db(db=db, question=question)
    return QuestionSchema.model_validate(created_question)

@router.post("/questions/with-answers/", response_model=DetailedQuestionSchema, status_code=status.HTTP_201_CREATED)
def create_question_with_answers_endpoint(
    question: QuestionWithAnswersCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_question_in_db(db=db, question=question)

@router.get("/questions/", response_model=List[DetailedQuestionSchema])
def get_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    questions = read_questions_from_db(db, skip=skip, limit=limit)
    return questions

@router.get("/questions/{question_id}", response_model=DetailedQuestionSchema)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Reading question with ID: %s", question_id)
    db_question = read_question_from_db(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return db_question

@router.put("/questions/{question_id}", response_model=DetailedQuestionSchema)
def update_question_endpoint(
    question_id: int,
    question: QuestionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_question = update_question_in_db(db, question_id, question)
    if db_question is None:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return db_question

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question_endpoint(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_question_from_db(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return None
