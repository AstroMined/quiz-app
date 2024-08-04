# filename: app/crud/crud_concepts.py

from sqlalchemy.orm import Session
from app.models.concepts import ConceptModel
from app.schemas.concepts import ConceptCreateSchema, ConceptUpdateSchema

def create_concept(db: Session, concept: ConceptCreateSchema) -> ConceptModel:
    db_concept = ConceptModel(**concept.model_dump())
    db.add(db_concept)
    db.commit()
    db.refresh(db_concept)
    return db_concept

def read_concept(db: Session, concept_id: int) -> ConceptModel:
    return db.query(ConceptModel).filter(ConceptModel.id == concept_id).first()

def read_concepts(db: Session, skip: int = 0, limit: int = 100) -> list[ConceptModel]:
    return db.query(ConceptModel).offset(skip).limit(limit).all()

def update_concept(db: Session, concept_id: int, concept: ConceptUpdateSchema) -> ConceptModel:
    db_concept = read_concept(db, concept_id)
    if db_concept:
        update_data = concept.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_concept, key, value)
        db.commit()
        db.refresh(db_concept)
    return db_concept

def delete_concept(db: Session, concept_id: int) -> bool:
    db_concept = read_concept(db, concept_id)
    if db_concept:
        db.delete(db_concept)
        db.commit()
        return True
    return False
