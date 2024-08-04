# filename: app/crud/crud_disciplines.py

from sqlalchemy.orm import Session
from app.models.disciplines import DisciplineModel
from app.schemas.disciplines import DisciplineCreateSchema, DisciplineUpdateSchema

def create_discipline(db: Session, discipline: DisciplineCreateSchema) -> DisciplineModel:
    db_discipline = DisciplineModel(**discipline.model_dump())
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def read_discipline(db: Session, discipline_id: int) -> DisciplineModel:
    return db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()

def read_disciplines(db: Session, skip: int = 0, limit: int = 100) -> list[DisciplineModel]:
    return db.query(DisciplineModel).offset(skip).limit(limit).all()

def update_discipline(db: Session, discipline_id: int, discipline: DisciplineUpdateSchema) -> DisciplineModel:
    db_discipline = read_discipline(db, discipline_id)
    if db_discipline:
        update_data = discipline.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_discipline, key, value)
        db.commit()
        db.refresh(db_discipline)
    return db_discipline

def delete_discipline(db: Session, discipline_id: int) -> bool:
    db_discipline = read_discipline(db, discipline_id)
    if db_discipline:
        db.delete(db_discipline)
        db.commit()
        return True
    return False