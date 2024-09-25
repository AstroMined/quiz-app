# filename: backend/app/api/endpoints/domains.py

"""
Domains Management API

This module provides API endpoints for managing domains in the quiz application.
It includes operations for creating, reading, updating, and deleting domains.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_domains module.

Endpoints:
- POST /domains/: Create a new domain
- GET /domains/: Retrieve a list of domains
- GET /domains/{domain_id}: Retrieve a specific domain by ID
- PUT /domains/{domain_id}: Update a specific domain
- DELETE /domains/{domain_id}: Delete a specific domain

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_domains import (
    create_domain_in_db,
    delete_domain_from_db,
    read_domain_from_db,
    read_domains_from_db,
    update_domain_in_db,
)
from backend.app.db.session import get_db
from backend.app.schemas.domains import (
    DomainCreateSchema,
    DomainSchema,
    DomainUpdateSchema,
)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()


@router.post("/domains/", response_model=DomainSchema, status_code=201)
def post_domain(
    request: Request, domain: DomainCreateSchema, db: Session = Depends(get_db)
):
    """
    Create a new domain.

    This endpoint allows authenticated users to create a new domain in the database.
    The domain data is validated using the DomainCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        domain (DomainCreateSchema): The domain data to be created.
        db (Session): The database session.

    Returns:
        DomainSchema: The created domain data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_domain = DomainCreateSchema(**domain.model_dump())
    domain_data = validated_domain.model_dump()
    created_domain = create_domain_in_db(db=db, domain_data=domain_data)
    return DomainSchema.model_validate(created_domain)


@router.get("/domains/", response_model=List[DomainSchema])
def get_domains(
    request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve a list of domains.

    This endpoint allows authenticated users to retrieve a paginated list of domains from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of domains to skip. Defaults to 0.
        limit (int, optional): The maximum number of domains to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[DomainSchema]: A list of domains.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    domains = read_domains_from_db(db, skip=skip, limit=limit)
    return [DomainSchema.model_validate(d) for d in domains]


@router.get("/domains/{domain_id}", response_model=DomainSchema)
def get_domain(request: Request, domain_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific domain by ID.

    This endpoint allows authenticated users to retrieve a single domain by its ID.

    Args:
        request (Request): The FastAPI request object.
        domain_id (int): The ID of the domain to retrieve.
        db (Session): The database session.

    Returns:
        DomainSchema: The domain data.

    Raises:
        HTTPException: If the domain with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_domain = read_domain_from_db(db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainSchema.model_validate(db_domain)


@router.put("/domains/{domain_id}", response_model=DomainSchema)
def put_domain(
    request: Request,
    domain_id: int,
    domain: DomainUpdateSchema,
    db: Session = Depends(get_db),
):
    """
    Update a specific domain.

    This endpoint allows authenticated users to update an existing domain by its ID.

    Args:
        request (Request): The FastAPI request object.
        domain_id (int): The ID of the domain to update.
        domain (DomainUpdateSchema): The updated domain data.
        db (Session): The database session.

    Returns:
        DomainSchema: The updated domain data.

    Raises:
        HTTPException: If the domain with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_domain = DomainUpdateSchema(**domain.model_dump())
    domain_data = validated_domain.model_dump()
    updated_domain = update_domain_in_db(db, domain_id, domain_data)
    if updated_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainSchema.model_validate(updated_domain)


@router.delete("/domains/{domain_id}", status_code=204)
def delete_domain(request: Request, domain_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific domain.

    This endpoint allows authenticated users to delete an existing domain by its ID.

    Args:
        request (Request): The FastAPI request object.
        domain_id (int): The ID of the domain to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the domain with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_domain_from_db(db, domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="Domain not found")
    return None
