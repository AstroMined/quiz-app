# filename: app/crud/crud_roles.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.schemas.roles import RoleCreateSchema, RoleUpdateSchema
from app.crud.crud_role_to_permission_associations import add_permission_to_role, remove_permission_from_role, get_role_permissions
from app.services.logging_service import logger

def create_role_crud(db: Session, role: RoleCreateSchema) -> RoleModel:
    db_role = RoleModel(name=role.name, description=role.description)
    logger.debug("Creating role: %s", db_role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    # Add permissions to the role
    for permission_id in role.permissions:
        logger.debug("Adding permission %s to role %s", permission_id, db_role.id)
        add_permission_to_role(db, db_role.id, permission_id)

    logger.debug("Role created with id %s, name %s, and permissions %s", db_role.id, db_role.name, db_role.permissions)
    return db_role

def read_role_crud(db: Session, role_id: int) -> RoleModel:
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with id {role_id} not found")
    return role

def read_roles_crud(db: Session, skip: int = 0, limit: int = 100) -> list[RoleModel]:
    return db.query(RoleModel).offset(skip).limit(limit).all()

def update_role_crud(db: Session, role_id: int, role: RoleUpdateSchema) -> RoleModel:
    db_role = read_role_crud(db, role_id)
    
    # Update basic fields
    for field, value in role.model_dump(exclude_unset=True).items():
        if field != "permissions":
            setattr(db_role, field, value)
    
    # Update permissions
    if role.permissions is not None:
        current_permissions = get_role_permissions(db, role_id)
        current_permission_names = {p.name for p in current_permissions}
        new_permission_names = set(role.permissions)

        # Remove permissions that are no longer associated
        for permission in current_permissions:
            if permission.name not in new_permission_names:
                remove_permission_from_role(db, role_id, permission.id)

        # Add new permissions
        for permission_name in new_permission_names:
            if permission_name not in current_permission_names:
                permission = db.query(PermissionModel).filter(PermissionModel.name == permission_name).first()
                if permission:
                    add_permission_to_role(db, role_id, permission.id)

    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role_crud(db: Session, role_id: int) -> bool:
    db_role = read_role_crud(db, role_id)
    db.delete(db_role)
    db.commit()
    return True
