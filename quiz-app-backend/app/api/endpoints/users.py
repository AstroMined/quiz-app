# filename: app/api/endpoints/users.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_user import create_user_in_db, update_user_in_db
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from app.services.logging_service import logger
from app.services.user_service import get_current_user

router = APIRouter()

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(
    user_data: dict, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_data['db'] = db
    user = UserCreateSchema(**user_data)
    try:
        new_user = create_user_in_db(db=db, user=user)
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
            ) from e

@router.get("/users/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    users = db.query(UserModel).all()
    return users

@router.get("/users/me", response_model=UserSchema)
def read_user_me(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user

@router.put(
    "/users/me",
    response_model=UserSchema,
)
def update_user_me(
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received user data: %s", user_data)

    # Add the database session to the schema data for validation
    user_data['db'] = db
    user_data['id'] = current_user.id
    logger.debug("User data after adding db: %s", user_data)

    # Manually create the schema instance with the updated data
    try:
        user_update = UserUpdateSchema(**user_data)
        logger.debug("Re-instantiated user update: %s", user_update)

        updated_user = update_user_in_db(db=db, user_id=current_user.id, updated_user=user_update)
        logger.debug("User updated successfully: %s", updated_user)
        return updated_user
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        logger.error("Error updating user: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)
