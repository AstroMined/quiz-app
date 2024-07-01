# filename: app/crud/crud_question_sets.py

from typing import List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.question_sets import QuestionSetModel
from app.models.groups import GroupModel
from app.models.questions import QuestionModel
from app.schemas.question_sets import QuestionSetCreateSchema, QuestionSetUpdateSchema
from app.services.logging_service import logger, sqlalchemy_obj_to_dict
from app.crud.crud_question_set_associations import (
    create_question_set_question_associations,
    create_question_set_group_associations,
    get_question_set_with_associations
)


def create_question_set_crud(
    db: Session,
    question_set: QuestionSetCreateSchema,
) -> QuestionSetModel:
    existing_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.name == question_set.name).first()
    if existing_question_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question set with name '{question_set.name}' already exists."
        )

    db_question_set = QuestionSetModel(
        name=question_set.name,
        is_public=question_set.is_public,
        creator_id=question_set.creator_id
    )
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)

    if question_set.question_ids:
        create_question_set_question_associations(db, db_question_set.id, question_set.question_ids)

    if question_set.group_ids:
        create_question_set_group_associations(db, db_question_set.id, question_set.group_ids)

    return get_question_set_with_associations(db, db_question_set.id)

def read_question_set_crud(db: Session, question_set_id: int) -> QuestionSetModel:
    question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    return question_set


def read_question_sets_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetModel]:
    question_sets = db.query(QuestionSetModel).offset(skip).limit(limit).all()
    if not question_sets:
        raise HTTPException(status_code=404, detail="No question sets found.")
    
    return question_sets

def update_question_set_crud(
    db: Session,
    question_set_id: int,
    question_set: QuestionSetUpdateSchema
) -> QuestionSetModel:
    logger.debug("Starting update for question set ID: %d", question_set_id)
    
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        logger.error("Question set with ID %d not found", question_set_id)
        raise HTTPException(
            status_code=404,
            detail=f"Question set with ID {question_set_id} not found."
        )

    update_data = question_set.model_dump(exclude_unset=True)
    logger.debug("Update data after model_dump: %s", update_data)
    
    # Update basic fields
    for field, value in update_data.items():
        if field not in ['question_ids', 'group_ids']:
            setattr(db_question_set, field, value)
            logger.debug("Set attribute %s to %s", field, value)

    # Update question associations
    if 'question_ids' in update_data:
        logger.debug("Updating question associations with IDs: %s", update_data['question_ids'])
        db_question_set.questions.clear()
        db.flush()
        create_question_set_question_associations(db, db_question_set.id, update_data['question_ids'])

    # Update group associations
    if 'group_ids' in update_data:
        logger.debug("Updating group associations with IDs: %s", update_data['group_ids'])
        db_question_set.groups.clear()
        db.flush()
        create_question_set_group_associations(db, db_question_set.id, update_data['group_ids'])

    db.commit()
    db.refresh(db_question_set)

    updated_question_set_dict = sqlalchemy_obj_to_dict(db_question_set)
    logger.debug("Updated question set: %s", updated_question_set_dict)

    return get_question_set_with_associations(db, db_question_set.id)

def delete_question_set_crud(db: Session, question_set_id: int) -> bool:
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    db.delete(db_question_set)
    db.commit()
    return True
