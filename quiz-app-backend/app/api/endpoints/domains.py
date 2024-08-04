# filename: app/api/endpoints/domains.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.domains import DomainSchema, DomainCreateSchema, DomainUpdateSchema
from app.crud.crud_domains import create_domain, read_domain, read_domains, update_domain, delete_domain
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/domains/", response_model=DomainSchema, status_code=201)
def post_domain(
    domain: DomainCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_domain(db=db, domain=domain)

@router.get("/domains/", response_model=List[DomainSchema])
def get_domains(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    domains = read_domains(db, skip=skip, limit=limit)
    return domains

@router.get("/domains/{domain_id}", response_model=DomainSchema)
def get_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_domain = read_domain(db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return db_domain

@router.put("/domains/{domain_id}", response_model=DomainSchema)
def put_domain(
    domain_id: int,
    domain: DomainUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_domain = update_domain(db, domain_id, domain)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return db_domain

@router.delete("/domains/{domain_id}", status_code=204)
def delete_domain_endpoint(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_domain(db, domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="Domain not found")
    return success
