# filename: app/crud/crud_user.py

from sqlalchemy.orm import Session
from app.models.users import UserModel
from app.models.groups import GroupModel
from app.models.roles import RoleModel
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.core.security import get_password_hash
from app.services.logging_service import logger

def create_user_crud(db: Session, user: UserCreateSchema) -> UserModel:
    hashed_password = get_password_hash(user.password)
    default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
    logger.debug("Default role: %s", default_role)
    user_role = user.role if user.role else default_role.name
    logger.debug("User role: %s", user_role)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        role=user_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_crud(db: Session, user_id: int, updated_user: UserUpdateSchema) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None
    update_data = updated_user.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    if "role" in update_data:
        setattr(user, "role", update_data["role"])
    for key, value in update_data.items():
        setattr(user, key, value)
    if updated_user.group_ids is not None:
        user.groups = db.query(GroupModel).filter(GroupModel.id.in_(updated_user.group_ids)).all()
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
