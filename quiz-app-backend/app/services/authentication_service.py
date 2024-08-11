# filename: app/services/authentication_service.py

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.users import UserModel
from app.crud.crud_user import read_user_by_username_from_db


def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = read_user_by_username_from_db(db, username)
    if not user:
        return False
    
    # Add this line to log the result of verify_password
    verification_result = verify_password(password, user.hashed_password)
    
    if not verification_result:
        hashed_attempt = get_password_hash(password)
        return False
    if not user.is_active:
        return False
    return user
