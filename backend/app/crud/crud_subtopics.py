# filename: backend/app/crud/crud_subtopics.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionToSubtopicAssociation,
                                             SubtopicToConceptAssociation,
                                             TopicToSubtopicAssociation)
from backend.app.models.concepts import ConceptModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def create_subtopic_in_db(db: Session, subtopic_data: Dict) -> SubtopicModel:
    db_subtopic = SubtopicModel(name=subtopic_data['name'])
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)

    if 'topic_ids' in subtopic_data and subtopic_data['topic_ids']:
        for topic_id in subtopic_data['topic_ids']:
            create_topic_to_subtopic_association_in_db(db, topic_id, db_subtopic.id)

    if 'concept_ids' in subtopic_data and subtopic_data['concept_ids']:
        for concept_id in subtopic_data['concept_ids']:
            create_subtopic_to_concept_association_in_db(db, db_subtopic.id, concept_id)

    if 'question_ids' in subtopic_data and subtopic_data['question_ids']:
        for question_id in subtopic_data['question_ids']:
            create_question_to_subtopic_association_in_db(db, question_id, db_subtopic.id)

    return db_subtopic

def read_subtopic_from_db(db: Session, subtopic_id: int) -> Optional[SubtopicModel]:
    return db.query(SubtopicModel).filter(SubtopicModel.id == subtopic_id).first()

def read_subtopic_by_name_from_db(db: Session, name: str) -> Optional[SubtopicModel]:
    return db.query(SubtopicModel).filter(SubtopicModel.name == name).first()

def read_subtopics_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[SubtopicModel]:
    return db.query(SubtopicModel).offset(skip).limit(limit).all()

def update_subtopic_in_db(db: Session, subtopic_id: int, subtopic_data: Dict) -> Optional[SubtopicModel]:
    db_subtopic = read_subtopic_from_db(db, subtopic_id)
    if db_subtopic:
        for key, value in subtopic_data.items():
            setattr(db_subtopic, key, value)
        db.commit()
        db.refresh(db_subtopic)
    return db_subtopic

def delete_subtopic_from_db(db: Session, subtopic_id: int) -> bool:
    db_subtopic = read_subtopic_from_db(db, subtopic_id)
    if db_subtopic:
        db.delete(db_subtopic)
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

def create_subtopic_to_concept_association_in_db(db: Session, subtopic_id: int, concept_id: int) -> bool:
    association = SubtopicToConceptAssociation(subtopic_id=subtopic_id, concept_id=concept_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_subtopic_to_concept_association_from_db(db: Session, subtopic_id: int, concept_id: int) -> bool:
    association = db.query(SubtopicToConceptAssociation).filter_by(
        subtopic_id=subtopic_id, concept_id=concept_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_to_subtopic_association_in_db(db: Session, question_id: int, subtopic_id: int) -> bool:
    association = QuestionToSubtopicAssociation(question_id=question_id, subtopic_id=subtopic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_subtopic_association_from_db(db: Session, question_id: int, subtopic_id: int) -> bool:
    association = db.query(QuestionToSubtopicAssociation).filter_by(
        question_id=question_id, subtopic_id=subtopic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_topics_for_subtopic_from_db(db: Session, subtopic_id: int) -> List[TopicModel]:
    return db.query(TopicModel).join(TopicToSubtopicAssociation).filter(
        TopicToSubtopicAssociation.subtopic_id == subtopic_id
    ).all()

def read_concepts_for_subtopic_from_db(db: Session, subtopic_id: int) -> List[ConceptModel]:
    return db.query(ConceptModel).join(SubtopicToConceptAssociation).filter(
        SubtopicToConceptAssociation.subtopic_id == subtopic_id
    ).all()

def read_questions_for_subtopic_from_db(db: Session, subtopic_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToSubtopicAssociation).filter(
        QuestionToSubtopicAssociation.subtopic_id == subtopic_id
    ).all()
