# filename: app/api/endpoints/question_sets.py

import json
from typing import List

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Response,
                     UploadFile, status)
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.crud.crud_question_sets import (create_question_set_in_db,
                                         delete_question_set_from_db,
                                         read_question_set_from_db,
                                         read_question_sets_from_db,
                                         update_question_set_in_db)
from app.crud.crud_questions import create_question_in_db
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.question_sets import (QuestionSetCreateSchema,
                                       QuestionSetSchema,
                                       QuestionSetUpdateSchema)
from app.schemas.questions import QuestionCreateSchema
from app.services.logging_service import logger, sqlalchemy_obj_to_dict
from app.services.user_service import get_current_user

router = APIRouter()


@router.post("/upload-questions/")
async def upload_question_set_endpoint(
    file: UploadFile = File(...),
    question_set_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can upload question sets")

    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        # Validate question data
        for question in question_data:
            # Validate question against schema
            question['db'] = db
            QuestionCreateSchema(**question)

        # Create question set with the provided name
        question_set = QuestionSetCreateSchema(name=question_set_name, db=db)
        question_set_created = create_question_set_in_db(db, question_set)

        # Create questions and associate with the newly created question set
        for question in question_data:
            question['question_set_id'] = question_set_created.id
            question['db'] = db
            create_question_in_db(db, QuestionCreateSchema(**question))

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON data: {str(exc)}"
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading question set: {str(exc)}"
        ) from exc

@router.get("/question-set/", response_model=List[QuestionSetSchema])
# pylint: disable=unused-argument
def read_questions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    questions = read_question_sets_from_db(db, skip=skip, limit=limit)
    return questions

@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def create_question_set_endpoint(
    question_set_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received question set data: %s", question_set_data)
    question_set_data['db'] = db
    question_set_data['creator_id'] = current_user.id
    if question_set_data.get('group_ids'):
        question_set_data['group_ids'] = list(set(question_set_data['group_ids']))

    # Add the database session to the schema data for validation
    logger.debug("Question set data after adding db: %s", question_set_data)

    # Manually create the schema instance with the updated data
    try:
        question_set = QuestionSetCreateSchema(**question_set_data)
        logger.debug("Re-instantiated question set: %s", question_set)

        created_question_set = create_question_set_in_db(db=db, question_set=question_set)
        logger.debug("Question set created successfully: %s", created_question_set)
        return created_question_set
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        logger.error("Error creating user response: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def get_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_set = read_question_set_from_db(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found")
    return question_set

@router.get("/question-sets/", response_model=List[QuestionSetSchema])
def read_question_sets_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_sets = read_question_sets_from_db(db, skip=skip, limit=limit)
    return question_sets

@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def update_question_set_endpoint(
    question_set_id: int,
    question_set_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received update data for question set %d: %s", question_set_id, question_set_data)
    question_set_data['db'] = db
    question_set_data['question_set_id'] = question_set_id
    question_set_data['creator_id'] = current_user.id
    if question_set_data.get('group_ids'):
        question_set_data['group_ids'] = list(set(question_set_data['group_ids']))
    if question_set_data.get('question_ids'):
        question_set_data['question_ids'] = list(set(question_set_data['question_ids']))

    try:
        question_set = QuestionSetUpdateSchema(**question_set_data)
        logger.debug("Re-instantiated question set for update: %s", question_set)

        updated_question_set = update_question_set_in_db(
            db,
            question_set_id=question_set_id,
            question_set=question_set
        )
        logger.debug("Updated question set: %s", sqlalchemy_obj_to_dict(updated_question_set))
        if updated_question_set is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")

        logger.debug("Question set updated successfully: %s", sqlalchemy_obj_to_dict(updated_question_set))
        
        response_data = {
            "id": updated_question_set.id,
            "name": updated_question_set.name,
            "is_public": updated_question_set.is_public,
            "creator_id": updated_question_set.creator_id,
            "question_ids": [question.id for question in updated_question_set.questions],
            "group_ids": [group.id for group in updated_question_set.groups]
        }
        
        return response_data
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        logger.error("Error updating question set: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    deleted = delete_question_set_from_db(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question set not found")
    return Response(status_code=204)
