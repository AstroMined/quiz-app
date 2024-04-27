# filename: app/api/endpoints/questions.py
"""
This module defines the API endpoint for retrieving questions in the application.

It includes an endpoint to retrieve a list of questions.
It also includes services to get the current user and a CRUD operation to get questions.

Imports:
----------
typing: For type hinting.
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
app.crud: For performing CRUD operations on the questions.
app.db: For getting the database session.
app.schemas: For validating and deserializing data.
app.services: For getting the current user.
app.models.users: For accessing the user model.

Variables:
----------
router: The API router instance.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud import get_questions_crud
from app.db import get_db
from app.schemas import QuestionSchema
from app.services import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.get("/questions/", response_model=List[QuestionSchema])
# pylint: disable=unused-argument
def get_questions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of questions.

    Parameters:
    - skip (int): Number of questions to skip (default: 0)
    - limit (int): Maximum number of questions to retrieve (default: 100)
    - db (Session): SQLAlchemy database session dependency
    - current_user (UserModel): Current authenticated user dependency

    Returns:
    - List[QuestionSchema]: List of questions retrieved from the database
    """
    questions = get_questions_crud(db, skip=skip, limit=limit)
    if not questions:
        return []
    return questions
