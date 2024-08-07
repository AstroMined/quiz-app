# filename: /code/quiz-app/quiz-app-backend/app/api/endpoints/answer_choices.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.answer_choices import AnswerChoiceSchema, AnswerChoiceCreateSchema, AnswerChoiceUpdateSchema
from app.crud.crud_answer_choices import (
    create_answer_choice_crud,
    read_answer_choice_crud,
    read_answer_choices_crud,
    update_answer_choice_crud,
    delete_answer_choice_crud
)
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/answer-choices/", response_model=AnswerChoiceSchema, status_code=status.HTTP_201_CREATED)
def create_answer_choice(
    answer_choice: AnswerChoiceCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_answer_choice_crud(db=db, answer_choice=answer_choice)

@router.get("/answer-choices/", response_model=List[AnswerChoiceSchema])
def get_answer_choices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return read_answer_choices_crud(db, skip=skip, limit=limit)

@router.get("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def get_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id=answer_choice_id)
    if db_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return db_answer_choice

@router.put("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def update_answer_choice(
    answer_choice_id: int,
    answer_choice: AnswerChoiceUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_answer_choice = update_answer_choice_crud(db, answer_choice_id, answer_choice)
    if db_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return db_answer_choice

@router.delete("/answer-choices/{answer_choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_answer_choice_crud(db, answer_choice_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return None
