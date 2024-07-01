# filename: app/crud/crud_question_tag_associations.py

from sqlalchemy.orm import Session
from app.models.associations import QuestionToTagAssociation
from app.models.questions import QuestionModel
from app.models.question_tags import QuestionTagModel


def add_tag_to_question(db: Session, question_id: int, tag_id: int):
    association = QuestionToTagAssociation(question_id=question_id, tag_id=tag_id)
    db.add(association)
    db.commit()

def remove_tag_from_question(db: Session, question_id: int, tag_id: int):
    db.query(QuestionToTagAssociation).filter_by(question_id=question_id, tag_id=tag_id).delete()
    db.commit()

def get_question_tags(db: Session, question_id: int):
    return db.query(QuestionTagModel).join(QuestionToTagAssociation).filter(QuestionToTagAssociation.question_id == question_id).all()

def get_questions_by_tag(db: Session, tag_id: int):
    return db.query(QuestionModel).join(QuestionToTagAssociation).filter(QuestionToTagAssociation.tag_id == tag_id).all()
