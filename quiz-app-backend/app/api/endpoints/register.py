# filename: app/api/endpoints/register.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.crud.crud_user import create_user, get_user_by_username
from app.db.session import get_db
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user.password = get_password_hash(user.password)
    return create_user(db=db, user=user)
