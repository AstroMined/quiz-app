# filename: app/api/endpoints/question.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.crud.crud_questions import (
    create_question_crud,
    read_question_crud,
    update_question_crud,
    delete_question_crud
)
from app.db.session import get_db
from app.schemas.answer_choices import AnswerChoiceSchema
from app.schemas.questions import (
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionSchema,
    QuestionTagSchema
)
from app.services.user_service import get_current_user
from app.models.users import UserModel


router = APIRouter()

@router.post("/question", response_model=QuestionSchema, status_code=201)
def create_question_endpoint(
    question_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_data['db'] = db
    question = QuestionCreateSchema(**question_data)
    db_question = create_question_crud(db, question)
    return db_question

@router.get("/question/question_id}", response_model=QuestionSchema)
# pylint: disable=unused-argument
def get_question_endpoint(
    question_id: int,
    question: QuestionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question = read_question_crud(db, question_id)
    return question

@router.put("/question/{question_id}", response_model=QuestionSchema)
def update_question_endpoint(
    question_id: int,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_data['db'] = db
    question = QuestionUpdateSchema(**question_data)
    db_question = update_question_crud(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return db_question

@router.delete("/question/{question_id}", status_code=204)
# pylint: disable=unused-argument
def delete_question_endpoint(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    deleted = delete_question_crud(db, question_id=question_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Question with ID {question_id} not found")
    return Response(status_code=204)
