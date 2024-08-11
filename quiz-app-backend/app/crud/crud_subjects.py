# filename: app/crud/crud_subjects.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.subjects import SubjectModel
from app.models.disciplines import DisciplineModel
from app.models.topics import TopicModel
from app.models.questions import QuestionModel
from app.models.associations import DisciplineToSubjectAssociation, SubjectToTopicAssociation, QuestionToSubjectAssociation

def create_subject_in_db(db: Session, subject_data: Dict) -> SubjectModel:
    db_subject = SubjectModel(name=subject_data['name'])
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def read_subject_from_db(db: Session, subject_id: int) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def read_subject_by_name_from_db(db: Session, name: str) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.name == name).first()

def read_subjects_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[SubjectModel]:
    return db.query(SubjectModel).offset(skip).limit(limit).all()

def update_subject_in_db(db: Session, subject_id: int, subject_data: Dict) -> Optional[SubjectModel]:
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        for key, value in subject_data.items():
            setattr(db_subject, key, value)
        db.commit()
        db.refresh(db_subject)
    return db_subject

def delete_subject_from_db(db: Session, subject_id: int) -> bool:
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False

def create_discipline_to_subject_association_in_db(db: Session, discipline_id: int, subject_id: int) -> bool:
    association = DisciplineToSubjectAssociation(discipline_id=discipline_id, subject_id=subject_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_discipline_to_subject_association_from_db(db: Session, discipline_id: int, subject_id: int) -> bool:
    association = db.query(DisciplineToSubjectAssociation).filter_by(
        discipline_id=discipline_id, subject_id=subject_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_subject_to_topic_association_in_db(db: Session, subject_id: int, topic_id: int) -> bool:
    association = SubjectToTopicAssociation(subject_id=subject_id, topic_id=topic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_subject_to_topic_association_from_db(db: Session, subject_id: int, topic_id: int) -> bool:
    association = db.query(SubjectToTopicAssociation).filter_by(
        subject_id=subject_id, topic_id=topic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_to_subject_association_in_db(db: Session, question_id: int, subject_id: int) -> bool:
    association = QuestionToSubjectAssociation(question_id=question_id, subject_id=subject_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_subject_association_from_db(db: Session, question_id: int, subject_id: int) -> bool:
    association = db.query(QuestionToSubjectAssociation).filter_by(
        question_id=question_id, subject_id=subject_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_disciplines_for_subject_from_db(db: Session, subject_id: int) -> List[DisciplineModel]:
    return db.query(DisciplineModel).join(DisciplineToSubjectAssociation).filter(
        DisciplineToSubjectAssociation.subject_id == subject_id
    ).all()

def read_topics_for_subject_from_db(db: Session, subject_id: int) -> List[TopicModel]:
    return db.query(TopicModel).join(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.subject_id == subject_id
    ).all()

def read_questions_for_subject_from_db(db: Session, subject_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToSubjectAssociation).filter(
        QuestionToSubjectAssociation.subject_id == subject_id
    ).all()
