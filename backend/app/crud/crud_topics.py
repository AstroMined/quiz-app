# filename: backend/app/crud/crud_topics.py

from typing import Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from backend.app.models.associations import (QuestionToTopicAssociation,
                                             SubjectToTopicAssociation,
                                             TopicToSubtopicAssociation)
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger


def create_topic_in_db(db: Session, topic_data: Dict) -> Optional[TopicModel]:
    # Validate subject IDs before creating the topic
    if 'subject_ids' in topic_data and topic_data['subject_ids']:
        for subject_id in topic_data['subject_ids']:
            subject = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
            if not subject:
                raise HTTPException(status_code=400, detail=f"Invalid subject_id: {subject_id}")

    db_topic = TopicModel(name=topic_data['name'])
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    if 'subject_ids' in topic_data and topic_data['subject_ids']:
        for subject_id in topic_data['subject_ids']:
            create_subject_to_topic_association_in_db(db, subject_id, db_topic.id)

    if 'subtopic_ids' in topic_data and topic_data['subtopic_ids']:
        for subtopic_id in topic_data['subtopic_ids']:
            create_topic_to_subtopic_association_in_db(db, db_topic.id, subtopic_id)

    if 'question_ids' in topic_data and topic_data['question_ids']:
        for question_id in topic_data['question_ids']:
            create_question_to_topic_association_in_db(db, question_id, db_topic.id)

    return db_topic

def read_topic_from_db(db: Session, topic_id: int) -> Optional[TopicModel]:
    topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if topic:
        # Manually load the subjects
        topic.subjects = read_subjects_for_topic_from_db(db, topic_id)
        logger.debug(f"Loaded subjects for topic: {topic.subjects}")
    return topic

def read_topic_by_name_from_db(db: Session, name: str) -> Optional[TopicModel]:
    return db.query(TopicModel).filter(TopicModel.name == name).first()

def read_topics_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[TopicModel]:
    return db.query(TopicModel).offset(skip).limit(limit).all()

def update_topic_in_db(db: Session, topic_id: int, topic_data: Dict) -> Optional[TopicModel]:
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        if 'name' in topic_data:
            db_topic.name = topic_data['name']

        if 'subject_ids' in topic_data:
            # Remove all existing associations
            db.query(SubjectToTopicAssociation).filter(SubjectToTopicAssociation.topic_id == topic_id).delete()

            # Create new associations
            for subject_id in topic_data['subject_ids']:
                if not db.query(SubjectModel).filter(SubjectModel.id == subject_id).first():
                    db.rollback()
                    return None
                create_subject_to_topic_association_in_db(db, subject_id, topic_id)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
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
        db.flush()
        logger.debug(f"Created association: subject_id={subject_id}, topic_id={topic_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create association: subject_id={subject_id}, topic_id={topic_id}. Error: {str(e)}")
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
        db.flush()
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
        db.flush()
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
    logger.debug(f"Querying subjects for topic_id: {topic_id}")
    subjects = db.query(SubjectModel).join(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.topic_id == topic_id
    ).all()
    logger.debug(f"Found subjects: {subjects}")
    
    # Additional debug: Check the SubjectToTopicAssociation table directly
    associations = db.query(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.topic_id == topic_id
    ).all()
    logger.debug(f"SubjectToTopicAssociations for topic_id {topic_id}: {associations}")
    
    return subjects

def read_subtopics_for_topic_from_db(db: Session, topic_id: int) -> List[SubtopicModel]:
    return db.query(SubtopicModel).join(TopicToSubtopicAssociation).filter(
        TopicToSubtopicAssociation.topic_id == topic_id
    ).all()

def read_questions_for_topic_from_db(db: Session, topic_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToTopicAssociation).filter(
        QuestionToTopicAssociation.topic_id == topic_id
    ).all()
