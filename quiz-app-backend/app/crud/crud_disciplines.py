# filename: app/crud/crud_disciplines.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.disciplines import DisciplineModel
from app.models.domains import DomainModel
from app.models.subjects import SubjectModel
from app.models.associations import DomainToDisciplineAssociation, DisciplineToSubjectAssociation

def create_discipline_in_db(db: Session, discipline_data: Dict) -> DisciplineModel:
    db_discipline = DisciplineModel(name=discipline_data['name'])
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def read_discipline_from_db(db: Session, discipline_id: int) -> Optional[DisciplineModel]:
    return db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()

def read_discipline_by_name_from_db(db: Session, name: str) -> Optional[DisciplineModel]:
    return db.query(DisciplineModel).filter(DisciplineModel.name == name).first()

def read_disciplines_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[DisciplineModel]:
    return db.query(DisciplineModel).offset(skip).limit(limit).all()

def update_discipline_in_db(db: Session, discipline_id: int, discipline_data: Dict) -> Optional[DisciplineModel]:
    db_discipline = read_discipline_from_db(db, discipline_id)
    if db_discipline:
        for key, value in discipline_data.items():
            setattr(db_discipline, key, value)
        db.commit()
        db.refresh(db_discipline)
    return db_discipline

def delete_discipline_from_db(db: Session, discipline_id: int) -> bool:
    db_discipline = read_discipline_from_db(db, discipline_id)
    if db_discipline:
        db.delete(db_discipline)
        db.commit()
        return True
    return False

def create_domain_to_discipline_association_in_db(db: Session, domain_id: int, discipline_id: int) -> bool:
    association = DomainToDisciplineAssociation(domain_id=domain_id, discipline_id=discipline_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_domain_to_discipline_association_from_db(db: Session, domain_id: int, discipline_id: int) -> bool:
    association = db.query(DomainToDisciplineAssociation).filter_by(
        domain_id=domain_id, discipline_id=discipline_id
    ).first()
    if association:
        db.delete(association)
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

def read_domains_for_discipline_from_db(db: Session, discipline_id: int) -> List[DomainModel]:
    return db.query(DomainModel).join(DomainToDisciplineAssociation).filter(
        DomainToDisciplineAssociation.discipline_id == discipline_id
    ).all()

def read_subjects_for_discipline_from_db(db: Session, discipline_id: int) -> List[SubjectModel]:
    return db.query(SubjectModel).join(DisciplineToSubjectAssociation).filter(
        DisciplineToSubjectAssociation.discipline_id == discipline_id
    ).all()
