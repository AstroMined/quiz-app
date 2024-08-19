# filename: backend/app/crud/crud_roles.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import RoleToPermissionAssociation
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def create_role_in_db(db: Session, role_data: Dict) -> RoleModel:
    db_role = RoleModel(
        name=role_data['name'],
        description=role_data.get('description'),
        default=role_data.get('default', False)
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def read_role_from_db(db: Session, role_id: int) -> Optional[RoleModel]:
    return db.query(RoleModel).filter(RoleModel.id == role_id).first()

def read_role_by_name_from_db(db: Session, name: str) -> Optional[RoleModel]:
    return db.query(RoleModel).filter(RoleModel.name == name).first()

def read_roles_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[RoleModel]:
    return db.query(RoleModel).offset(skip).limit(limit).all()

def update_role_in_db(db: Session, role_id: int, role_data: Dict) -> Optional[RoleModel]:
    db_role = read_role_from_db(db, role_id)
    if db_role:
        for key, value in role_data.items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role_from_db(db: Session, role_id: int) -> bool:
    db_role = read_role_from_db(db, role_id)
    if db_role:
        db.delete(db_role)
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

def read_permissions_for_role_from_db(db: Session, role_id: int) -> List[PermissionModel]:
    return db.query(PermissionModel).join(RoleToPermissionAssociation).filter(
        RoleToPermissionAssociation.role_id == role_id
    ).all()

def read_users_for_role_from_db(db: Session, role_id: int) -> List[UserModel]:
    return db.query(UserModel).filter(UserModel.role_id == role_id).all()
