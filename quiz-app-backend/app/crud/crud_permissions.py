# filename: app/crud/crud_permissions.py

from sqlalchemy.orm import Session
from app.models.permissions import PermissionModel
from app.schemas.permissions import PermissionCreateSchema, PermissionUpdateSchema


def create_permission_crud(db: Session, permission: PermissionCreateSchema) -> PermissionModel:
    db_permission = PermissionModel(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def read_permission_crud(db: Session, permission_id: int) -> PermissionModel:
    return db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()

def read_permissions_crud(db: Session, skip: int = 0, limit: int = 100) -> list[PermissionModel]:
    return db.query(PermissionModel).offset(skip).limit(limit).all()

def update_permission_crud(db: Session, permission_id: int, permission: PermissionUpdateSchema) -> PermissionModel:
    db_permission = read_permission_crud(db, permission_id)
    if db_permission:
        update_data = permission.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_permission, key, value)
        db.commit()
        db.refresh(db_permission)
    return db_permission

def delete_permission_crud(db: Session, permission_id: int) -> bool:
    db_permission = read_permission_crud(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False
