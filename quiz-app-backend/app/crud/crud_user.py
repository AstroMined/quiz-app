# filename: app/crud/crud_user.py

from sqlalchemy.orm import Session
from app.models import UserModel
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.core import get_password_hash

def create_user_crud(db: Session, user: UserCreateSchema) -> UserModel:
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_crud(db: Session, user_id: int, updated_user: UserUpdateSchema) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None
    update_data = updated_user.dict(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user_crud(db: Session, user_id: int) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None
