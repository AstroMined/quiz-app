# filename: backend/app/crud/crud_permissions.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import RoleToPermissionAssociation
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel


def create_permission_in_db(db: Session, permission_data: Dict) -> PermissionModel:
    db_permission = PermissionModel(
        name=permission_data['name'],
        description=permission_data.get('description')
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def read_permission_from_db(db: Session, permission_id: int) -> Optional[PermissionModel]:
    return db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()

def read_permission_by_name_from_db(db: Session, name: str) -> Optional[PermissionModel]:
    return db.query(PermissionModel).filter(PermissionModel.name == name).first()

def read_permissions_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[PermissionModel]:
    return db.query(PermissionModel).offset(skip).limit(limit).all()

def update_permission_in_db(db: Session, permission_id: int, permission_data: Dict) -> Optional[PermissionModel]:
    db_permission = read_permission_from_db(db, permission_id)
    if db_permission:
        for key, value in permission_data.items():
            setattr(db_permission, key, value)
        db.commit()
        db.refresh(db_permission)
    return db_permission

def delete_permission_from_db(db: Session, permission_id: int) -> bool:
    db_permission = read_permission_from_db(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False

def create_role_to_permission_association_in_db(db: Session, role_id: int, permission_id: int) -> bool:
    association = RoleToPermissionAssociation(role_id=role_id, permission_id=permission_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_role_to_permission_association_from_db(db: Session, role_id: int, permission_id: int) -> bool:
    association = db.query(RoleToPermissionAssociation).filter_by(
        role_id=role_id, permission_id=permission_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_roles_for_permission_from_db(db: Session, permission_id: int) -> List[RoleModel]:
    return db.query(RoleModel).join(RoleToPermissionAssociation).filter(
        RoleToPermissionAssociation.permission_id == permission_id
    ).all()
