# filename: backend/app/crud/crud_subjects.py

from typing import Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.associations import (DisciplineToSubjectAssociation,
                                             QuestionToSubjectAssociation,
                                             SubjectToTopicAssociation)
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger


def create_subject_in_db(db: Session, subject_data: Dict) -> SubjectModel:
    # Validate discipline IDs before creating the subject
    if 'discipline_ids' in subject_data and subject_data['discipline_ids']:
        for discipline_id in subject_data['discipline_ids']:
            discipline = db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()
            if not discipline:
                raise HTTPException(status_code=400, detail=f"Invalid discipline_id: {discipline_id}")

    db_subject = SubjectModel(name=subject_data['name'])
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)

    if 'discipline_ids' in subject_data and subject_data['discipline_ids']:
        for discipline_id in subject_data['discipline_ids']:
            create_discipline_to_subject_association_in_db(db, discipline_id, db_subject.id)

    if 'topic_ids' in subject_data and subject_data['topic_ids']:
        for topic_id in subject_data['topic_ids']:
            create_subject_to_topic_association_in_db(db, db_subject.id, topic_id)

    if 'question_ids' in subject_data and subject_data['question_ids']:
        for question_id in subject_data['question_ids']:
            create_question_to_subject_association_in_db(db, question_id, db_subject.id)

    return db_subject

def read_subject_from_db(db: Session, subject_id: int) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def read_subject_by_name_from_db(db: Session, name: str) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.name == name).first()

def read_subjects_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[SubjectModel]:
    return db.query(SubjectModel).offset(skip).limit(limit).all()

def update_subject_in_db(db: Session, subject_id: int, subject_data: Dict) -> Optional[SubjectModel]:
    logger.debug(f"Updating subject with id {subject_id}. Data: {subject_data}")
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        logger.debug(f"Found subject: {db_subject}")
        if 'name' in subject_data:
            db_subject.name = subject_data['name']

        if 'discipline_ids' in subject_data:
            logger.debug(f"Updating disciplines for subject {subject_id}")
            # Validate discipline IDs before updating
            for discipline_id in subject_data['discipline_ids']:
                discipline = db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()
                if not discipline:
                    logger.error(f"Discipline not found: {discipline_id}")
                    raise HTTPException(status_code=404, detail=f"Discipline not found: {discipline_id}")

            # Remove all existing associations
            db.query(DisciplineToSubjectAssociation).filter(DisciplineToSubjectAssociation.subject_id == subject_id).delete()

            # Create new associations
            for discipline_id in subject_data['discipline_ids']:
                create_discipline_to_subject_association_in_db(db, discipline_id, subject_id)

        try:
            db.commit()
            logger.debug(f"Successfully updated subject {subject_id}")
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError while updating subject {subject_id}: {str(e)}")
            raise HTTPException(status_code=400, detail="Subject with this name already exists")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while updating subject {subject_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        db.refresh(db_subject)
    else:
        logger.error(f"Subject not found: {subject_id}")
        raise HTTPException(status_code=404, detail="Subject not found")
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
