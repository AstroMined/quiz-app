# filename: backend/app/api/endpoints/questions.py

"""
Question Management API

This module provides API endpoints for managing questions in the quiz application.
It includes operations for creating, reading, updating, and deleting questions,
as well as specialized endpoints for creating questions with associated answers.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_questions module.

Endpoints:
- POST /questions/: Create a new question
- POST /questions/with-answers/: Create a new question with associated answers
- GET /questions/: Retrieve a list of questions
- GET /questions/{question_id}: Retrieve a specific question by ID
- PUT /questions/{question_id}: Update a specific question
- DELETE /questions/{question_id}: Delete a specific question

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_questions import (create_question_in_db,
                                             delete_question_from_db,
                                             read_question_from_db,
                                             read_questions_from_db,
                                             update_question_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.questions import (DetailedQuestionSchema,
                                           QuestionCreateSchema,
                                           QuestionSchema,
                                           QuestionUpdateSchema,
                                           QuestionWithAnswersCreateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/questions/", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
async def post_question(
    question: QuestionCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> QuestionSchema:
    """
    Create a new question.

    This endpoint allows authenticated users to create a new question in the database.
    The question data is validated using the QuestionCreateSchema.

    Args:
        question (QuestionCreateSchema): The question data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionSchema: The created question data.

    Raises:
        HTTPException: 
            - 422 Unprocessable Entity: If the question data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during question creation.
    """
    try:
        validated_question = QuestionCreateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
        created_question = create_question_in_db(db=db, question_data=question_data)
        return QuestionSchema.model_validate(created_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(ve)
                        ) from ve
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while creating the question"
                        ) from e

@router.post("/questions/with-answers/",
             response_model=DetailedQuestionSchema,
             status_code=status.HTTP_201_CREATED)
async def post_question_with_answers(
    question: QuestionWithAnswersCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> DetailedQuestionSchema:
    """
    Create a new question with associated answers.

    This endpoint allows authenticated users to create a new question along with its answer choices
    in a single operation.
    The question and answer data are validated using the QuestionWithAnswersCreateSchema.

    Args:
        question (QuestionWithAnswersCreateSchema): The question and answer data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        DetailedQuestionSchema: The created question data including associated answers.

    Raises:
        HTTPException: 
            - 422 Unprocessable Entity: If the question or answer data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during question creation.
    """
    try:
        validated_question = QuestionWithAnswersCreateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
        created_question = create_question_in_db(db=db, question_data=question_data)
        return DetailedQuestionSchema.model_validate(created_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(ve)
                        ) from ve
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while creating the question with answers"
                        ) from e

@router.get("/questions/", response_model=List[DetailedQuestionSchema])
async def get_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> List[DetailedQuestionSchema]:
    """
    Retrieve a list of questions.

    This endpoint allows authenticated users to retrieve a
    paginated list of questions from the database.

    Args:
        skip (int, optional): The number of questions to skip. Defaults to 0.
        limit (int, optional): The maximum number of questions to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[DetailedQuestionSchema]: A list of questions with their details.

    Raises:
        HTTPException: 500 Internal Server Error if an unexpected error occurs during retrieval.
    """
    try:
        questions = read_questions_from_db(db, skip=skip, limit=limit)
        return [DetailedQuestionSchema.model_validate(q) for q in questions]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while retrieving questions"
                        ) from e

@router.get("/questions/{question_id}", response_model=DetailedQuestionSchema)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> DetailedQuestionSchema:
    """
    Retrieve a specific question by ID.

    This endpoint allows authenticated users to retrieve a single question by its ID.

    Args:
        question_id (int): The ID of the question to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        DetailedQuestionSchema: The detailed question data.

    Raises:
        HTTPException: 
            - 404 Not Found: If the question with the given ID does not exist.
            - 500 Internal Server Error: If an unexpected error occurs during retrieval.
    """
    try:
        db_question = read_question_from_db(db, question_id=question_id)
        if db_question is None:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return DetailedQuestionSchema.model_validate(db_question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while retrieving the question"
                        ) from e

@router.put("/questions/{question_id}", response_model=DetailedQuestionSchema)
async def put_question(
    question_id: int,
    question: QuestionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> DetailedQuestionSchema:
    """
    Update a specific question.

    This endpoint allows authenticated users to update an existing question by its ID.

    Args:
        question_id (int): The ID of the question to update.
        question (QuestionUpdateSchema): The updated question data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        DetailedQuestionSchema: The updated question data.

    Raises:
        HTTPException: 
            - 404 Not Found: If the question with the given ID does not exist.
            - 422 Unprocessable Entity: If the update data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during the update.
    """
    try:
        validated_question = QuestionUpdateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
        updated_question = update_question_in_db(db, question_id, question_data)
        if updated_question is None:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return DetailedQuestionSchema.model_validate(updated_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(ve)
                        ) from ve
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while updating the question"
                        ) from e

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific question.

    This endpoint allows authenticated users to delete an existing question by its ID.

    Args:
        question_id (int): The ID of the question to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: 
            - 404 Not Found: If the question with the given ID does not exist.
            - 500 Internal Server Error: If an unexpected error occurs during the deletion.
    """
    try:
        success = delete_question_from_db(db, question_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while deleting the question"
                        ) from e
