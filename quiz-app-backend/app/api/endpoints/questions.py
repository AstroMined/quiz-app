# filename: app/api/endpoints/questions.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.crud_questions import read_questions_crud
from app.db.session import get_db
from app.schemas.questions import QuestionSchema
from app.services.user_service import get_current_user
from app.models.users import UserModel


router = APIRouter()

@router.get("/questions/", response_model=List[QuestionSchema])
def get_questions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    questions = read_questions_crud(db, skip=skip, limit=limit)
    if not questions:
        return []
    return questions
