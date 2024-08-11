# filename: app/api/endpoints/subjects.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.crud_subjects import (create_subject_in_db, delete_subject_from_db,
                                    read_subject_from_db, read_subjects_from_db,
                                    update_subject_in_db)
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.subjects import (SubjectCreateSchema, SubjectSchema,
                                  SubjectUpdateSchema)
from app.services.user_service import get_current_user

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def post_subject(
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_subject_in_db(db=db, subject=subject)

@router.get("/subjects/", response_model=List[SubjectSchema])
def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subjects = read_subjects_from_db(db, skip=skip, limit=limit)
    return subjects

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subject = read_subject_from_db(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def put_subject(
    subject_id: int,
    subject: SubjectUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subject = update_subject_in_db(db, subject_id, subject)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_subject_from_db(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return success
