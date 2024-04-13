# filename: app/api/endpoints/users.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import UserModel
from app.crud import create_user_crud, update_user_crud
from app.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from app.services import get_current_user

router = APIRouter()

@router.get("/users/", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    users = db.query(UserModel).all()
    return users

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        new_user = create_user_crud(db=db, user=user)
        return new_user
    except Exception as e:
        # If there's an error (e.g., username already exists), raise an HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
            ) from e

@router.get("/users/me", response_model=UserSchema)
def read_user_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.put("/users/me", response_model=UserSchema)
def update_user_me(updated_user: UserUpdateSchema, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_crud(db=db, user_id=current_user.id, updated_user=updated_user)
