# filename: app/crud/crud_question_tags.py

from sqlalchemy.orm import Session
from app.models.question_tags import QuestionTagModel
from app.schemas.question_tags import QuestionTagCreateSchema


def create_question_tag_crud(db: Session, question_tag: QuestionTagCreateSchema) -> QuestionTagModel:
    db_question_tag = QuestionTagModel(**question_tag.model_dump())
    db.add(db_question_tag)
    db.commit()
    db.refresh(db_question_tag)
    return db_question_tag

def get_question_tag_by_id_crud(db: Session, question_tag_id: int) -> QuestionTagModel:
    return db.query(QuestionTagModel).filter(QuestionTagModel.id == question_tag_id).first()

def get_question_tag_by_tag_crud(db: Session, tag: str) -> QuestionTagModel:
    return db.query(QuestionTagModel).filter(QuestionTagModel.tag == tag).first()

def update_question_tag_crud(db: Session, question_tag_id: int, updated_tag: str) -> QuestionTagModel:
    db_question_tag = get_question_tag_by_id_crud(db, question_tag_id)
    if db_question_tag:
        db_question_tag.tag = updated_tag
        db.commit()
        db.refresh(db_question_tag)
    return db_question_tag

def delete_question_tag_crud(db: Session, question_tag_id: int) -> None:
    db_question_tag = get_question_tag_by_id_crud(db, question_tag_id)
    if db_question_tag:
        db.delete(db_question_tag)
        db.commit()