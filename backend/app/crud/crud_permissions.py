# filename: backend/app/crud/crud_permissions.py

"""
This module handles CRUD operations for permissions in the database.

It provides functions for creating, reading, updating, and deleting permissions,
as well as managing associations between roles and permissions.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models.associations: For RoleToPermissionAssociation
- backend.app.models.permissions: For the PermissionModel
- backend.app.models.roles: For the RoleModel

Main functions:
- create_permission_in_db: Creates a new permission
- read_permission_from_db: Retrieves a single permission by ID
- read_permission_by_name_from_db: Retrieves a single permission by name
- read_permissions_from_db: Retrieves multiple permissions with pagination
- update_permission_in_db: Updates an existing permission
- delete_permission_from_db: Deletes a permission
- create_role_to_permission_association_in_db: Associates a role with a permission
- delete_role_to_permission_association_from_db: Removes a role-permission association
- read_roles_for_permission_from_db: Retrieves roles for a permission

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_permissions import create_permission_in_db

    def add_new_permission(db: Session, name: str, description: str):
        permission_data = {"name": name, "description": description}
        return create_permission_in_db(db, permission_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.associations import RoleToPermissionAssociation
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.services.logging_service import logger


def create_permission_in_db(db: Session, permission_data: Dict) -> PermissionModel:
    """
    Create a new permission in the database.

    Args:
        db (Session): The database session.
        permission_data (Dict): A dictionary containing the permission data.
            Required keys: "name"
            Optional keys: "description"

    Returns:
        PermissionModel: The created permission database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        permission_data = {
            "name": "create_user",
            "description": "Allows creation of new users"
        }
        new_permission = create_permission_in_db(db, permission_data)
    """
    db_permission = PermissionModel(
        name=permission_data["name"], description=permission_data.get("description")
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def read_permission_from_db(
    db: Session, permission_id: int
) -> Optional[PermissionModel]:
    """
    Retrieve a single permission from the database by its ID.

    Args:
        db (Session): The database session.
        permission_id (int): The ID of the permission to retrieve.

    Returns:
        Optional[PermissionModel]: The retrieved permission database object,
        or None if not found.

    Usage example:
        permission = read_permission_from_db(db, 1)
        if permission:
            print(f"Permission name: {permission.name}")
    """
    return db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()


def read_permission_by_name_from_db(
    db: Session, name: str
) -> Optional[PermissionModel]:
    """
    Retrieve a single permission from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the permission to retrieve.

    Returns:
        Optional[PermissionModel]: The retrieved permission database object,
        or None if not found.

    Usage example:
        permission = read_permission_by_name_from_db(db, "create_user")
        if permission:
            print(f"Permission ID: {permission.id}")
    """
    return db.query(PermissionModel).filter(PermissionModel.name == name).first()


def read_permissions_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[PermissionModel]:
    """
    Retrieve a list of permissions from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[PermissionModel]: A list of retrieved permission database objects.

    Usage example:
        permissions = read_permissions_from_db(db, skip=10, limit=20)
        for permission in permissions:
            print(f"Permission: {permission.name}")
    """
    return db.query(PermissionModel).offset(skip).limit(limit).all()


def update_permission_in_db(
    db: Session, permission_id: int, permission_data: Dict
) -> Optional[PermissionModel]:
    """
    Update an existing permission in the database.

    Args:
        db (Session): The database session.
        permission_id (int): The ID of the permission to update.
        permission_data (Dict): A dictionary containing the updated permission data.

    Returns:
        Optional[PermissionModel]: The updated permission database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"name": "update_user", "description": "Allows updating user information"}
        updated_permission = update_permission_in_db(db, 1, updated_data)
        if updated_permission:
            print(f"Updated permission name: {updated_permission.name}")
    """
    db_permission = read_permission_from_db(db, permission_id)
    if db_permission:
        for key, value in permission_data.items():
            setattr(db_permission, key, value)
        db.commit()
        db.refresh(db_permission)
    return db_permission


def delete_permission_from_db(db: Session, permission_id: int) -> bool:
    """
    Delete a permission from the database.

    Args:
        db (Session): The database session.
        permission_id (int): The ID of the permission to delete.

    Returns:
        bool: True if the permission was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_permission_from_db(db, 1):
            print("Permission successfully deleted")
        else:
            print("Permission not found or couldn't be deleted")
    """
    db_permission = read_permission_from_db(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False


def create_role_to_permission_association_in_db(
    db: Session, role_id: int, permission_id: int
) -> bool:
    """
    Create an association between a role and a permission in the database.

    Args:
        db (Session): The database session.
        role_id (int): The ID of the role.
        permission_id (int): The ID of the permission.

    Returns:
        bool: True if the association was successfully created, False if it already exists.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_role_to_permission_association_in_db(db, 1, 2):
            print("Role-permission association created successfully")
        else:
            print("Association already exists or failed to create")
    """
    # Check if association already exists
    existing_association = (
        db.query(RoleToPermissionAssociation)
        .filter_by(role_id=role_id, permission_id=permission_id)
        .first()
    )
    if existing_association:
        return False  # Association already exists
    
    association = RoleToPermissionAssociation(
        role_id=role_id, permission_id=permission_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as e:
        logger.exception("Error creating role-permission association: %s", e)
        db.rollback()
        return False


def delete_role_to_permission_association_from_db(
    db: Session, role_id: int, permission_id: int
) -> bool:
    """
    Delete an association between a role and a permission from the database.

    Args:
        db (Session): The database session.
        role_id (int): The ID of the role.
        permission_id (int): The ID of the permission.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_role_to_permission_association_from_db(db, 1, 2):
            print("Role-permission association deleted successfully")
        else:
            print("Role-permission association not found or couldn't be deleted")
    """
    association = (
        db.query(RoleToPermissionAssociation)
        .filter_by(role_id=role_id, permission_id=permission_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_roles_for_permission_from_db(
    db: Session, permission_id: int
) -> List[RoleModel]:
    """
    Retrieve all roles associated with a specific permission from the database.

    Args:
        db (Session): The database session.
        permission_id (int): The ID of the permission.

    Returns:
        List[RoleModel]: A list of role database objects associated with the permission.

    Usage example:
        roles = read_roles_for_permission_from_db(db, 1)
        for role in roles:
            print(f"Role with permission 1: {role.name}")
    """
    return (
        db.query(RoleModel)
        .join(RoleToPermissionAssociation)
        .filter(RoleToPermissionAssociation.permission_id == permission_id)
        .all()
    )
