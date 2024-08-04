# filename: app/api/endpoints/concepts.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.concepts import ConceptSchema, ConceptCreateSchema, ConceptUpdateSchema
from app.crud.crud_concepts import create_concept, read_concept, read_concepts, update_concept, delete_concept
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/concepts/", response_model=ConceptSchema, status_code=201)
def post_concept(
    concept: ConceptCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_concept(db=db, concept=concept)

@router.get("/concepts/", response_model=List[ConceptSchema])
def get_concepts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    concepts = read_concepts(db, skip=skip, limit=limit)
    return concepts

@router.get("/concepts/{concept_id}", response_model=ConceptSchema)
def get_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_concept = read_concept(db, concept_id=concept_id)
    if db_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return db_concept

@router.put("/concepts/{concept_id}", response_model=ConceptSchema)
def put_concept(
    concept_id: int,
    concept: ConceptUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_concept = update_concept(db, concept_id, concept)
    if db_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return db_concept

@router.delete("/concepts/{concept_id}", status_code=204)
def delete_concept_endpoint(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_concept(db, concept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Concept not found")
    return success
