# filename: app/crud/crud_role_to_permission_associations.py

from sqlalchemy.orm import Session
from app.models.associations import RoleToPermissionAssociation
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.services.logging_service import logger

def add_permission_to_role(db: Session, role_id: int, permission_id: int | str):
    if isinstance(permission_id, str):
        # If permission_id is a string, query the PermissionModel to get the actual permission ID
        permission = db.query(PermissionModel).filter(PermissionModel.name == permission_id).first()
        if not permission:
            raise ValueError(f"Permission with name '{permission_id}' not found")
        permission_id = permission.id

    association = RoleToPermissionAssociation(role_id=role_id, permission_id=permission_id)
    db.add(association)
    db.commit()

def remove_permission_from_role(db: Session, role_id: int, permission_id: int):
    db.query(RoleToPermissionAssociation).filter_by(role_id=role_id, permission_id=permission_id).delete()
    db.commit()

def get_role_permissions(db: Session, role_id: int):
    return db.query(PermissionModel).join(RoleToPermissionAssociation).filter(RoleToPermissionAssociation.role_id == role_id).all()

def get_roles_by_permission(db: Session, permission_id: int):
    return db.query(RoleModel).join(RoleToPermissionAssociation).filter(RoleToPermissionAssociation.permission_id == permission_id).all()
