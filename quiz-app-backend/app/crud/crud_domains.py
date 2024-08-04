# filename: app/crud/crud_domains.py

from sqlalchemy.orm import Session
from app.models.domains import DomainModel
from app.schemas.domains import DomainCreateSchema, DomainUpdateSchema

def create_domain(db: Session, domain: DomainCreateSchema) -> DomainModel:
    db_domain = DomainModel(**domain.model_dump())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

def read_domain(db: Session, domain_id: int) -> DomainModel:
    return db.query(DomainModel).filter(DomainModel.id == domain_id).first()

def read_domains(db: Session, skip: int = 0, limit: int = 100) -> list[DomainModel]:
    return db.query(DomainModel).offset(skip).limit(limit).all()

def update_domain(db: Session, domain_id: int, domain: DomainUpdateSchema) -> DomainModel:
    db_domain = read_domain(db, domain_id)
    if db_domain:
        update_data = domain.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_domain, key, value)
        db.commit()
        db.refresh(db_domain)
    return db_domain

def delete_domain(db: Session, domain_id: int) -> bool:
    db_domain = read_domain(db, domain_id)
    if db_domain:
        db.delete(db_domain)
        db.commit()
        return True
    return False
