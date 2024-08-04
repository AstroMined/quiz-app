# filename: app/api/endpoints/register.py
"""
This module provides an endpoint for user registration.

It defines a route for registering new users by validating 
the provided data and creating a new user in the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.services.user_service import get_user_by_username, get_user_by_email
from app.crud.crud_user import create_user_crud
from app.db.session import get_db
from app.schemas.user import UserCreateSchema
from app.models.roles import RoleModel
from app.services.logging_service import logger

router = APIRouter()

@router.post("/register", status_code=201)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    logger.info(f"Registering user: {user.username}")
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        logger.error(f"Username already registered: {user.username}")
        raise HTTPException(status_code=422, detail="Username already registered")
    db_email = get_user_by_email(db, email=user.email)
    if db_email:
        logger.error(f"Email already registered: {user.email}")
        raise HTTPException(status_code=422, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    logger.debug(f"Hashed password for user {user.username}: {hashed_password}")
    if not user.role:
        default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
        user.role = default_role.name
        logger.debug(f"Default role assigned: {user.role}")
    user_create = UserCreateSchema(
        username=user.username,
        password=hashed_password,  # Pass the hashed password here
        email=user.email,
        role=user.role
    )
    created_user = create_user_crud(db=db, user=user_create)
    logger.debug(f"User registered: {user.username}")
    return created_user
