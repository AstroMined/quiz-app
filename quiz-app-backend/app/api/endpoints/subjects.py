# filename: app/api/endpoints/subjects.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.subjects import SubjectSchema, SubjectCreateSchema
from app.crud import create_subject_crud, read_subject_crud, update_subject_crud, delete_subject_crud

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def create_subject_endpoint(subject: SubjectCreateSchema, db: Session = Depends(get_db)):
    return create_subject_crud(db=db, subject=subject)

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def read_subject_endpoint(subject_id: int, db: Session = Depends(get_db)):
    subject = read_subject_crud(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def update_subject_endpoint(subject_id: int, subject: SubjectCreateSchema, db: Session = Depends(get_db)):
    updated_subject = update_subject_crud(db, subject_id, subject)
    if not updated_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return updated_subject

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject_endpoint(subject_id: int, db: Session = Depends(get_db)):
    deleted = delete_subject_crud(db, subject_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None
