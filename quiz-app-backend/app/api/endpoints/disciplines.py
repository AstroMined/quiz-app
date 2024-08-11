# filename: app/api/endpoints/disciplines.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.crud_disciplines import (create_discipline_in_db, delete_discipline_from_db,
                                       read_discipline_from_db, read_disciplines_from_db,
                                       update_discipline_in_db)
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.disciplines import (DisciplineCreateSchema, DisciplineSchema,
                                     DisciplineUpdateSchema)
from app.services.user_service import get_current_user

router = APIRouter()

@router.post("/disciplines/", response_model=DisciplineSchema, status_code=201)
def post_discipline(
    discipline: DisciplineCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_discipline_in_db(db=db, discipline=discipline)

@router.get("/disciplines/", response_model=List[DisciplineSchema])
def get_disciplines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    disciplines = read_disciplines_from_db(db, skip=skip, limit=limit)
    return disciplines

@router.get("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def get_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_discipline = read_discipline_from_db(db, discipline_id=discipline_id)
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
    db_discipline = update_discipline_in_db(db, discipline_id, discipline)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return db_discipline

@router.delete("/disciplines/{discipline_id}", status_code=204)
def delete_discipline_endpoint(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_discipline_from_db(db, discipline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return success
