# filename: backend/app/crud/crud_domains.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import DomainToDisciplineAssociation
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel


def create_domain_in_db(db: Session, domain_data: Dict) -> DomainModel:
    db_domain = DomainModel(name=domain_data['name'])
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

def read_domain_from_db(db: Session, domain_id: int) -> Optional[DomainModel]:
    return db.query(DomainModel).filter(DomainModel.id == domain_id).first()

def read_domain_by_name_from_db(db: Session, name: str) -> Optional[DomainModel]:
    return db.query(DomainModel).filter(DomainModel.name == name).first()

def read_domains_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[DomainModel]:
    return db.query(DomainModel).offset(skip).limit(limit).all()

def update_domain_in_db(db: Session, domain_id: int, domain_data: Dict) -> Optional[DomainModel]:
    db_domain = read_domain_from_db(db, domain_id)
    if db_domain:
        for key, value in domain_data.items():
            setattr(db_domain, key, value)
        db.commit()
        db.refresh(db_domain)
    return db_domain

def delete_domain_from_db(db: Session, domain_id: int) -> bool:
    db_domain = read_domain_from_db(db, domain_id)
    if db_domain:
        db.delete(db_domain)
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

def read_disciplines_for_domain_from_db(db: Session, domain_id: int) -> List[DisciplineModel]:
    return db.query(DisciplineModel).join(DomainToDisciplineAssociation).filter(
        DomainToDisciplineAssociation.domain_id == domain_id
    ).all()
