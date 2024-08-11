# filename: app/api/endpoints/register.py
"""
This module provides an endpoint for user registration.

It defines a route for registering new users by validating 
the provided data and creating a new user in the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.crud.crud_user import create_user_in_db, read_user_by_email_from_db, read_user_by_username_from_db
from app.db.session import get_db
from app.models.roles import RoleModel
from app.schemas.user import UserCreateSchema

router = APIRouter()

@router.post("/register", status_code=201)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    db_user = read_user_by_username_from_db(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=422, detail="Username already registered")
    db_email = read_user_by_email_from_db(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=422, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    if not user.role:
        default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
        user.role = default_role.name
    user_create = UserCreateSchema(
        username=user.username,
        password=hashed_password,  # Pass the hashed password here
        email=user.email,
        role=user.role
    )
    created_user = create_user_in_db(db=db, user=user_create)
    return created_user
