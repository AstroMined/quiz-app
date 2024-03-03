# filename: app/crud/crud_user.py
from app.schemas.user import UserCreate, UserLogin
from sqlalchemy.orm import Session
from app.models.users import User
from app.core.security import verify_password, get_password_hash

def create_user(db: Session, user: UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
