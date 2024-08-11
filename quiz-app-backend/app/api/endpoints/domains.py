# filename: app/api/endpoints/domains.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.crud_domains import (create_domain_in_db, delete_domain_from_db, read_domain_from_db,
                                   read_domains_from_db, update_domain_in_db)
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.domains import (DomainCreateSchema, DomainSchema,
                                 DomainUpdateSchema)
from app.services.user_service import get_current_user

router = APIRouter()

@router.post("/domains/", response_model=DomainSchema, status_code=201)
def post_domain(
    domain: DomainCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_domain_in_db(db=db, domain=domain)

@router.get("/domains/", response_model=List[DomainSchema])
def get_domains(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    domains = read_domains_from_db(db, skip=skip, limit=limit)
    return domains

@router.get("/domains/{domain_id}", response_model=DomainSchema)
def get_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_domain = read_domain_from_db(db, domain_id=domain_id)
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
    db_domain = update_domain_in_db(db, domain_id, domain)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return db_domain

@router.delete("/domains/{domain_id}", status_code=204)
def delete_domain_endpoint(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_domain_from_db(db, domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="Domain not found")
    return success
