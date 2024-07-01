# filename: app/crud/crud_question_set_associations.py

from typing import List
from sqlalchemy.orm import Session
from app.models.associations import QuestionSetToQuestionAssociation, QuestionSetToGroupAssociation
from app.models.question_sets import QuestionSetModel


def create_question_set_question_associations(db: Session, question_set_id: int, question_ids: List[int]):
    associations = [
        QuestionSetToQuestionAssociation(question_set_id=question_set_id, question_id=q_id)
        for q_id in question_ids
    ]
    db.add_all(associations)
    db.commit()

def create_question_set_group_associations(db: Session, question_set_id: int, group_ids: List[int]):
    associations = [
        QuestionSetToGroupAssociation(question_set_id=question_set_id, group_id=g_id)
        for g_id in group_ids
    ]
    db.add_all(associations)
    db.commit()

def get_question_set_with_associations(db: Session, question_set_id: int) -> QuestionSetModel:
    return db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
