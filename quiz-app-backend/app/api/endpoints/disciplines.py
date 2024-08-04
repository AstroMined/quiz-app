# filename: app/api/endpoints/disciplines.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.disciplines import DisciplineSchema, DisciplineCreateSchema, DisciplineUpdateSchema
from app.crud.crud_disciplines import create_discipline, read_discipline, read_disciplines, update_discipline, delete_discipline
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/disciplines/", response_model=DisciplineSchema, status_code=201)
def post_discipline(
    discipline: DisciplineCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_discipline(db=db, discipline=discipline)

@router.get("/disciplines/", response_model=List[DisciplineSchema])
def get_disciplines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    disciplines = read_disciplines(db, skip=skip, limit=limit)
    return disciplines

@router.get("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def get_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_discipline = read_discipline(db, discipline_id=discipline_id)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return db_discipline

@router.put("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def put_discipline(
    discipline_id: int,
    discipline: DisciplineUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_discipline = update_discipline(db, discipline_id, discipline)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return db_discipline

@router.delete("/disciplines/{discipline_id}", status_code=204)
def delete_discipline_endpoint(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_discipline(db, discipline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return success
