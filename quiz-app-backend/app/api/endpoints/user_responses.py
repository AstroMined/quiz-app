# filename: app/api/endpoints/user_responses.py

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from app.crud import (
    create_user_response_crud,
    get_user_response_crud,
    get_user_responses_crud,
    update_user_response_crud,
    delete_user_response_crud
)
from app.db import get_db
from app.schemas import UserResponseSchema, UserResponseCreateSchema, UserResponseUpdateSchema
from app.models import AnswerChoiceModel, UserModel, QuestionModel

router = APIRouter()

@router.post("/user-responses/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def create_user_response_endpoint(user_response: UserResponseCreateSchema, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_response.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id")

    question = db.query(QuestionModel).filter(QuestionModel.id == user_response.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question_id")

    answer_choice = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == user_response.answer_choice_id).first()
    if not answer_choice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid answer_choice_id")

    return create_user_response_crud(db=db, user_response=user_response)

@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def get_user_response_endpoint(user_response_id: int, db: Session = Depends(get_db)):
    user_response = get_user_response_crud(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User response not found")
    return user_response

@router.get("/user-responses/", response_model=List[UserResponseSchema])
def get_user_responses_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_responses = get_user_responses_crud(db, skip=skip, limit=limit)
    return user_responses

@router.put("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def update_user_response_endpoint(user_response_id: int, user_response: UserResponseUpdateSchema, db: Session = Depends(get_db)):
    updated_user_response = update_user_response_crud(db, user_response_id, user_response)
    return updated_user_response

@router.delete("/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_response_endpoint(user_response_id: int, db: Session = Depends(get_db)):
    delete_user_response_crud(db, user_response_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
