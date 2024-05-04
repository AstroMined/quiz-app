# filename: app/crud/crud_user_utils.py

from sqlalchemy.orm import Session
from app.models import UserModel

def get_user_by_username_crud(db: Session, username: str) -> UserModel:
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_email_crud(db: Session, email: str) -> UserModel:
    return db.query(UserModel).filter(UserModel.email == email).first()
