# filename: app/api/endpoints/question_sets.py
"""
This module defines the API endpoints for managing question sets in the application.

It includes endpoints to create, read, update, and delete question sets.
It also includes a service to get the current user and a CRUD operation to create a question.

Imports:
----------
json: For parsing and generating JSON data.
typing: For type hinting.
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
pydantic: For data validation and serialization.
app.db: For getting the database session.
app.services: For getting the current user.
app.models: For accessing the user and question set models.
app.crud: For performing CRUD operations on the question sets.
app.schemas: For validating and deserializing data.

Variables:
----------
router: The API router instance.
"""

import json
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Response,
    status
)
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.db import get_db
from app.services import get_current_user
from app.models import UserModel
from app.crud import (
    create_question_crud,
    read_question_sets_crud,
    read_question_set_crud,
    update_question_set_crud,
    delete_question_set_crud,
    create_question_set_crud
)
from app.schemas import (
    QuestionSetSchema,
    QuestionSetCreateSchema,
    QuestionSetUpdateSchema,
    QuestionCreateSchema
)

router = APIRouter()


@router.post("/upload-questions/")
async def upload_question_set_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function uploads a question set to the database.

    Parameters:
    ----------
    file: UploadFile
        The file containing the question set to be uploaded.
    db: Session
        The database session.

    Raises:
    ----------
    HTTPException
        If there is an error while uploading the question set.

    Returns:
    ----------
    dict
        A message indicating that the question set has been successfully uploaded.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can upload question sets")

    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        # Validate question data
        for question in question_data:
            # Validate question against schema
            QuestionCreateSchema(**question)

        # Create question set
        question_set = QuestionSetCreateSchema(name=file.filename)
        question_set_created = create_question_set_crud(db, question_set)

        # Create questions and associate with question set
        for question in question_data:
            question['question_set_id'] = question_set_created.id
            create_question_crud(db, QuestionCreateSchema(**question))

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid JSON data: {str(exc)}") from exc

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error uploading question set: {str(exc)}") from exc


@router.get("/question-set/", response_model=List[QuestionSetSchema])
# pylint: disable=unused-argument
def read_questions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function retrieves a list of questions from the database.

    Parameters:
    ----------
    skip: int
        The number of records to skip.
    limit: int
        The maximum number of records to return.
    db: Session
        The database session.

    Returns:
    ----------
    List[QuestionSetSchema]
        A list of questions.
    """
    questions = read_question_sets_crud(db, skip=skip, limit=limit)
    return questions


@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def create_question_set_endpoint(
    question_set: QuestionSetCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function retrieves a list of questions from the database.

    Parameters:
    ----------
    skip: int
        The number of records to skip.
    limit: int
        The maximum number of records to return.
    db: Session
        The database session.

    Returns:
    ----------
    List[QuestionSetSchema]
        A list of questions.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can create question sets")

    return create_question_set_crud(db=db, question_set=question_set)


@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
# pylint: disable=unused-argument
def get_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function retrieves a question set from the database by its ID.

    Parameters:
    ----------
    question_set_id: int
        The ID of the question set to retrieve.
    db: Session
        The database session.

    Raises:
    ----------
    HTTPException
        If the question set with the provided ID is not found.

    Returns:
    ----------
    QuestionSetSchema
        The retrieved question set.
    """
    question_set = read_question_set_crud(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question set with ID {question_set_id} not found")
    return question_set


@router.get("/question-sets/", response_model=List[QuestionSetSchema])
# pylint: disable=unused-argument
def read_question_sets_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function retrieves a list of question sets from the database.

    Parameters:
    ----------
    skip: int
        The number of records to skip.
    limit: int
        The maximum number of records to return.
    db: Session
        The database session.

    Returns:
    ----------
    List[QuestionSetSchema]
        A list of question sets.
    """
    question_sets = read_question_sets_crud(db, skip=skip, limit=limit)
    return question_sets


@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def update_question_set_endpoint(
    question_set_id: int,
    question_set: QuestionSetUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function updates a question set in the database.

    Parameters:
    ----------
    question_set_id: int
        The ID of the question set to update.
    question_set: QuestionSetUpdateSchema
        The updated question set.
    db: Session
        The database session.
    current_user: UserModel
        The current user.

    Raises:
    ----------
    HTTPException
        If the current user is not an admin or the question set with the provided ID is not found.

    Returns:
    ----------
    QuestionSetSchema
        The updated question set.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can update question sets")

    db_question_set = update_question_set_crud(
        db, question_set_id=question_set_id, question_set=question_set)
    if db_question_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Question set not found")
    return QuestionSetSchema(
        id=db_question_set.id,
        name=db_question_set.name,
        is_public=db_question_set.is_public,
        question_ids=db_question_set.question_ids
    )


@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function deletes a question set from the database.

    Parameters:
    ----------
    question_set_id: int
        The ID of the question set to delete.
    db: Session
        The database session.
    current_user: UserModel
        The current user.

    Raises:
    ----------
    HTTPException
        If the current user is not an admin or the question set with the provided ID is not found.

    Returns:
    ----------
    Response
        An HTTP response with a 204 status code.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can delete question sets")

    deleted = delete_question_set_crud(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Question set not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
