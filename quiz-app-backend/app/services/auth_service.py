# filename: app/services/auth_service.py

from sqlalchemy.orm import Session
from app.crud.crud_user_utils import get_user_by_username_crud
from app.core import verify_password
from app.models import UserModel

def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = get_user_by_username_crud(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user
