# filename: app/api/endpoints/subjects.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.subjects import SubjectSchema, SubjectCreateSchema, SubjectUpdateSchema
from app.crud.crud_subjects import create_subject, read_subject, read_subjects, update_subject, delete_subject
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def post_subject(
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_subject(db=db, subject=subject)

@router.get("/subjects/", response_model=List[SubjectSchema])
def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subjects = read_subjects(db, skip=skip, limit=limit)
    return subjects

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subject = read_subject(db, subject_id=subject_id)
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
    db_subject = update_subject(db, subject_id, subject)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_subject(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return success
