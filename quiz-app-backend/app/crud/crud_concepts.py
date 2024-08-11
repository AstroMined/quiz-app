# filename: app/crud/crud_concepts.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.concepts import ConceptModel
from app.models.subtopics import SubtopicModel
from app.models.questions import QuestionModel
from app.models.associations import SubtopicToConceptAssociation, QuestionToConceptAssociation

def create_concept_in_db(db: Session, concept_data: Dict) -> ConceptModel:
    db_concept = ConceptModel(name=concept_data['name'])
    db.add(db_concept)
    db.commit()
    db.refresh(db_concept)
    return db_concept

def read_concept_from_db(db: Session, concept_id: int) -> Optional[ConceptModel]:
    return db.query(ConceptModel).filter(ConceptModel.id == concept_id).first()

def read_concept_by_name_from_db(db: Session, name: str) -> Optional[ConceptModel]:
    return db.query(ConceptModel).filter(ConceptModel.name == name).first()

def read_concepts_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[ConceptModel]:
    return db.query(ConceptModel).offset(skip).limit(limit).all()

def update_concept_in_db(db: Session, concept_id: int, concept_data: Dict) -> Optional[ConceptModel]:
    db_concept = read_concept_from_db(db, concept_id)
    if db_concept:
        for key, value in concept_data.items():
            setattr(db_concept, key, value)
        db.commit()
        db.refresh(db_concept)
    return db_concept

def delete_concept_from_db(db: Session, concept_id: int) -> bool:
    db_concept = read_concept_from_db(db, concept_id)
    if db_concept:
        db.delete(db_concept)
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

def create_question_to_concept_association_in_db(db: Session, question_id: int, concept_id: int) -> bool:
    association = QuestionToConceptAssociation(question_id=question_id, concept_id=concept_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_concept_association_from_db(db: Session, question_id: int, concept_id: int) -> bool:
    association = db.query(QuestionToConceptAssociation).filter_by(
        question_id=question_id, concept_id=concept_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_subtopics_for_concept_from_db(db: Session, concept_id: int) -> List[SubtopicModel]:
    return db.query(SubtopicModel).join(SubtopicToConceptAssociation).filter(
        SubtopicToConceptAssociation.concept_id == concept_id
    ).all()

def read_questions_for_concept_from_db(db: Session, concept_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToConceptAssociation).filter(
        QuestionToConceptAssociation.concept_id == concept_id
    ).all()
