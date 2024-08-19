# filename: backend/app/crud/crud_topics.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionToTopicAssociation,
                                             SubjectToTopicAssociation,
                                             TopicToSubtopicAssociation)
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def create_topic_in_db(db: Session, topic_data: Dict) -> TopicModel:
    db_topic = TopicModel(name=topic_data['name'])
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def read_topic_from_db(db: Session, topic_id: int) -> Optional[TopicModel]:
    return db.query(TopicModel).filter(TopicModel.id == topic_id).first()

def read_topic_by_name_from_db(db: Session, name: str) -> Optional[TopicModel]:
    return db.query(TopicModel).filter(TopicModel.name == name).first()

def read_topics_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[TopicModel]:
    return db.query(TopicModel).offset(skip).limit(limit).all()

def update_topic_in_db(db: Session, topic_id: int, topic_data: Dict) -> Optional[TopicModel]:
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        for key, value in topic_data.items():
            setattr(db_topic, key, value)
        db.commit()
        db.refresh(db_topic)
    return db_topic

def delete_topic_from_db(db: Session, topic_id: int) -> bool:
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        db.delete(db_topic)
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

def create_topic_to_subtopic_association_in_db(db: Session, topic_id: int, subtopic_id: int) -> bool:
    association = TopicToSubtopicAssociation(topic_id=topic_id, subtopic_id=subtopic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_topic_to_subtopic_association_from_db(db: Session, topic_id: int, subtopic_id: int) -> bool:
    association = db.query(TopicToSubtopicAssociation).filter_by(
        topic_id=topic_id, subtopic_id=subtopic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_to_topic_association_in_db(db: Session, question_id: int, topic_id: int) -> bool:
    association = QuestionToTopicAssociation(question_id=question_id, topic_id=topic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_topic_association_from_db(db: Session, question_id: int, topic_id: int) -> bool:
    association = db.query(QuestionToTopicAssociation).filter_by(
        question_id=question_id, topic_id=topic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_subjects_for_topic_from_db(db: Session, topic_id: int) -> List[SubjectModel]:
    return db.query(SubjectModel).join(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.topic_id == topic_id
    ).all()

def read_subtopics_for_topic_from_db(db: Session, topic_id: int) -> List[SubtopicModel]:
    return db.query(SubtopicModel).join(TopicToSubtopicAssociation).filter(
        TopicToSubtopicAssociation.topic_id == topic_id
    ).all()

def read_questions_for_topic_from_db(db: Session, topic_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToTopicAssociation).filter(
        QuestionToTopicAssociation.topic_id == topic_id
    ).all()
