# filename: backend/app/api/endpoints/register.py

"""
User Registration API

This module provides an API endpoint for user registration in the quiz application.
It includes an operation for creating a new user account.

The module uses FastAPI for defining the API endpoint and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_user module.

Endpoints:
- POST /register: Register a new user

This endpoint does not require authentication as it's used for creating new user accounts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.crud.crud_user import (
    create_user_in_db,
    read_user_by_email_from_db,
    read_user_by_username_from_db,
)
from backend.app.db.session import get_db
from backend.app.models.roles import RoleModel
from backend.app.schemas.user import UserCreateSchema, UserSchema
from backend.app.services.logging_service import logger

router = APIRouter()


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint allows new users to create an account in the application.
    It checks if the username and email are unique, hashes the password,
    and assigns a default role if one is not specified.

    Args:
        user (UserCreateSchema): The user data for registration.
        db (Session): The database session.

    Returns:
        UserSchema: The created user data.

    Raises:
        HTTPException:
            - 400 Bad Request: If the username or email is already registered.
            - 400 Bad Request: If the specified role_id does not exist.
            - 400 Bad Request: If no role is available (neither specified nor default).
            - 500 Internal Server Error: For any other unexpected errors.
    """
    try:
        logger.debug(f"Attempting to register user: {user.username}")

        db_user = read_user_by_username_from_db(db, username=user.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        db_email = read_user_by_email_from_db(db, email=user.email)
        if db_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        logger.debug("Hashing password")
        hashed_password = get_password_hash(user.password.get_secret_value())
        logger.debug("Password hashed successfully")

        if user.role_id is not None:
            logger.debug(f"Checking for role with id: {user.role_id}")
            role = db.query(RoleModel).filter(RoleModel.id == user.role_id).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role_id: {user.role_id}",
                )
        else:
            logger.debug("No role_id provided, looking for default role")
            default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
            if default_role:
                user.role_id = default_role.id
                logger.debug(f"Assigned default role with id: {user.role_id}")
            else:
                logger.debug("No default role found")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No role available for user creation",
                )

        user_data = user.model_dump()
        user_data["hashed_password"] = hashed_password
        del user_data["password"]

        logger.debug("Creating user in database")
        created_user = create_user_in_db(db=db, user_data=user_data)
        logger.debug(f"User created successfully with id: {created_user.id}")

        return UserSchema.model_validate(created_user)
    except ValidationError as exc:
        logger.error(f"Validation error during user registration: {exc}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {exc}",
        ) from exc
    except ValueError as exc:
        logger.error(f"Error during user registration: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error during user registration: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {exc}",
        ) from exc
