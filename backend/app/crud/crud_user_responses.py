# filename: backend/app/crud/crud_user_responses.py

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.user_responses import UserResponseModel


def create_user_response_in_db(db: Session, user_response_data: Dict) -> UserResponseModel:
    db_user_response = UserResponseModel(
        user_id=user_response_data['user_id'],
        question_id=user_response_data['question_id'],
        answer_choice_id=user_response_data['answer_choice_id'],
        is_correct=user_response_data['is_correct'],
        response_time=user_response_data.get('response_time'),
        timestamp=user_response_data.get('timestamp', datetime.now(timezone.utc))
    )
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def read_user_response_from_db(db: Session, user_response_id: int) -> Optional[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()

def read_user_responses_from_db(
    db: Session,
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[UserResponseModel]:
    query = db.query(UserResponseModel)
    if user_id:
        query = query.filter(UserResponseModel.user_id == user_id)
    if question_id:
        query = query.filter(UserResponseModel.question_id == question_id)
    if start_time:
        query = query.filter(UserResponseModel.timestamp >= start_time)
    if end_time:
        query = query.filter(UserResponseModel.timestamp <= end_time)
    return query.offset(skip).limit(limit).all()

def update_user_response_in_db(db: Session, user_response_id: int, user_response_data: Dict) -> Optional[UserResponseModel]:
    db_user_response = read_user_response_from_db(db, user_response_id)
    if db_user_response:
        for key, value in user_response_data.items():
            if key != 'is_correct' or value is not None:  # Only update is_correct if it's explicitly set
                setattr(db_user_response, key, value)
        db.commit()
        db.refresh(db_user_response)
    return db_user_response

def delete_user_response_from_db(db: Session, user_response_id: int) -> bool:
    db_user_response = read_user_response_from_db(db, user_response_id)
    if db_user_response:
        db.delete(db_user_response)
        db.commit()
        return True
    return False

def read_user_responses_for_user_from_db(db: Session, user_id: int) -> List[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.user_id == user_id).all()

def read_user_responses_for_question_from_db(db: Session, question_id: int) -> List[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.question_id == question_id).all()
