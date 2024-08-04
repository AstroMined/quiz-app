# filename: app/api/endpoints/subtopics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.subtopics import SubtopicSchema, SubtopicCreateSchema, SubtopicUpdateSchema
from app.crud.crud_subtopics import create_subtopic, read_subtopic, read_subtopics, update_subtopic, delete_subtopic
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/subtopics/", response_model=SubtopicSchema, status_code=201)
def post_subtopic(
    subtopic: SubtopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_subtopic(db=db, subtopic=subtopic)

@router.get("/subtopics/", response_model=List[SubtopicSchema])
def get_subtopics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subtopics = read_subtopics(db, skip=skip, limit=limit)
    return subtopics

@router.get("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def get_subtopic(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subtopic = read_subtopic(db, subtopic_id=subtopic_id)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return db_subtopic

@router.put("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def put_subtopic(
    subtopic_id: int,
    subtopic: SubtopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subtopic = update_subtopic(db, subtopic_id, subtopic)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return db_subtopic

@router.delete("/subtopics/{subtopic_id}", status_code=204)
def delete_subtopic_endpoint(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_subtopic(db, subtopic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return success
