# filename: backend/app/crud/crud_roles.py

"""
This module handles CRUD operations for roles in the database.

It provides functions for creating, reading, updating, and deleting roles,
as well as managing associations between roles and permissions.

Key dependencies:
- sqlalchemy.orm: For database session management
- sqlalchemy.exc: For handling IntegrityError
- backend.app.models.associations: For RoleToPermissionAssociation
- backend.app.models.permissions: For the PermissionModel
- backend.app.models.roles: For the RoleModel
- backend.app.models.users: For the UserModel

Main functions:
- create_role_in_db: Creates a new role
- read_role_from_db: Retrieves a single role by ID
- read_role_by_name_from_db: Retrieves a single role by name
- read_roles_from_db: Retrieves multiple roles with pagination
- update_role_in_db: Updates an existing role
- delete_role_from_db: Deletes a role
- create_role_to_permission_association_in_db: Associates a role with a permission
- delete_role_to_permission_association_from_db: Removes a role-permission association
- read_permissions_for_role_from_db: Retrieves permissions for a role
- read_users_for_role_from_db: Retrieves users for a role
- read_default_role_from_db: Retrieves the default role

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_roles import create_role_in_db

    def add_new_role(db: Session, name: str, description: str, is_default: bool = False):
        role_data = {"name": name, "description": description, "default": is_default}
        return create_role_in_db(db, role_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import RoleToPermissionAssociation
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import logger


def create_role_in_db(db: Session, role_data: Dict) -> RoleModel:
    """
    Create a new role in the database.

    Args:
        db (Session): The database session.
        role_data (Dict): A dictionary containing the role data.
            Required keys: "name"
            Optional keys: "description", "default", "permissions"

    Returns:
        RoleModel: The created role database object.

    Raises:
        IntegrityError: If attempting to create a default role when one already exists.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        role_data = {
            "name": "Admin",
            "description": "Administrator role",
            "default": False,
            "permissions": ["create_user", "delete_user"]
        }
        new_role = create_role_in_db(db, role_data)
    """
    is_default = role_data.get("default", False)
    if is_default:
        existing_default = db.query(RoleModel).filter(RoleModel.default == True).first()
        if existing_default:
            raise IntegrityError(
                "A default role already exists", params=None, orig=None
            )

    db_role = RoleModel(
        name=role_data["name"],
        description=role_data.get("description"),
        default=is_default,
    )
    db.add(db_role)
    db.flush()  # Flush to get the role ID

    # Handle permissions
    if "permissions" in role_data:
        for permission_name in role_data["permissions"]:
            permission = (
                db.query(PermissionModel)
                .filter(PermissionModel.name == permission_name)
                .first()
            )
            if permission:
                association = RoleToPermissionAssociation(
                    role_id=db_role.id, permission_id=permission.id
                )
                db.add(association)

    db.commit()
    db.refresh(db_role)
    return db_role


def read_role_from_db(db: Session, role_id: int) -> Optional[RoleModel]:
    """
    Retrieve a single role from the database by its ID.

    Args:
        db (Session): The database session.
        role_id (int): The ID of the role to retrieve.

    Returns:
        Optional[RoleModel]: The retrieved role database object,
        or None if not found.

    Usage example:
        role = read_role_from_db(db, 1)
        if role:
            print(f"Role name: {role.name}")
    """
    return db.query(RoleModel).filter(RoleModel.id == role_id).first()


def read_role_by_name_from_db(db: Session, name: str) -> Optional[RoleModel]:
    """
    Retrieve a single role from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the role to retrieve.

    Returns:
        Optional[RoleModel]: The retrieved role database object,
        or None if not found.

    Usage example:
        role = read_role_by_name_from_db(db, "Admin")
        if role:
            print(f"Role ID: {role.id}")
    """
    return db.query(RoleModel).filter(RoleModel.name == name).first()


def read_roles_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[RoleModel]:
    """
    Retrieve a list of roles from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[RoleModel]: A list of retrieved role database objects.

    Usage example:
        roles = read_roles_from_db(db, skip=10, limit=20)
        for role in roles:
            print(f"Role: {role.name}")
    """
    return db.query(RoleModel).offset(skip).limit(limit).all()


def update_role_in_db(
    db: Session, role_id: int, role_data: Dict
) -> Optional[RoleModel]:
    """
    Update an existing role in the database.

    Args:
        db (Session): The database session.
        role_id (int): The ID of the role to update.
        role_data (Dict): A dictionary containing the updated role data.
            Optional keys: "name", "description", "default", "permissions"

    Returns:
        Optional[RoleModel]: The updated role database object,
        or None if not found.

    Raises:
        IntegrityError: If attempting to set a role as default when another default role exists.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {
            "name": "Super Admin",
            "description": "Super administrator role",
            "permissions": ["create_user", "delete_user", "manage_roles"]
        }
        updated_role = update_role_in_db(db, 1, updated_data)
        if updated_role:
            print(f"Updated role name: {updated_role.name}")
    """
    db_role = read_role_from_db(db, role_id)
    if db_role:
        if "default" in role_data and role_data["default"]:
            existing_default = (
                db.query(RoleModel)
                .filter(RoleModel.default is True, RoleModel.id != role_id)
                .first()
            )
            if existing_default:
                raise IntegrityError(
                    "A default role already exists", params=None, orig=None
                )

        for key, value in role_data.items():
            if key != "permissions":
                setattr(db_role, key, value)

        # Handle permissions
        if "permissions" in role_data:
            # Remove existing permissions
            db.query(RoleToPermissionAssociation).filter(
                RoleToPermissionAssociation.role_id == role_id
            ).delete()

            # Add new permissions
            for permission_name in role_data["permissions"]:
                permission = (
                    db.query(PermissionModel)
                    .filter(PermissionModel.name == permission_name)
                    .first()
                )
                if permission:
                    association = RoleToPermissionAssociation(
                        role_id=db_role.id, permission_id=permission.id
                    )
                    db.add(association)

        db.commit()
        db.refresh(db_role)
    return db_role


def delete_role_from_db(db: Session, role_id: int) -> bool:
    """
    Delete a role from the database.

    Args:
        db (Session): The database session.
        role_id (int): The ID of the role to delete.

    Returns:
        bool: True if the role was successfully deleted, False otherwise.

    Raises:
        ValueError: If no default role is found to reassign users.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_role_from_db(db, 1):
            print("Role successfully deleted")
        else:
            print("Role not found or couldn't be deleted")
    """
    db_role = read_role_from_db(db, role_id)
    if not db_role:
        return False

    # Find a default role to reassign users
    default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
    if not default_role:
        raise ValueError("No default role found to reassign users")

    # Reassign users to the default role
    db.query(UserModel).filter(UserModel.role_id == role_id).update(
        {UserModel.role_id: default_role.id}
    )

    # Delete the role
    db.delete(db_role)
    db.commit()
    return True



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
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_role_to_permission_association_in_db(db, 1, 2):
            print("Role-permission association created successfully")
        else:
            print("Failed to create role-permission association")
    """
    association = RoleToPermissionAssociation(
        role_id=role_id, permission_id=permission_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error creating role-permission association: %s", str(e))
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


def read_permissions_for_role_from_db(
    db: Session, role_id: int
) -> List[PermissionModel]:
    """
    Retrieve all permissions associated with a specific role from the database.

    Args:
        db (Session): The database session.
        role_id (int): The ID of the role.

    Returns:
        List[PermissionModel]: A list of permission database objects associated with the role.

    Usage example:
        permissions = read_permissions_for_role_from_db(db, 1)
        for permission in permissions:
            print(f"Permission for role 1: {permission.name}")
    """
    return (
        db.query(PermissionModel)
        .join(RoleToPermissionAssociation)
        .filter(RoleToPermissionAssociation.role_id == role_id)
        .all()
    )


def read_users_for_role_from_db(db: Session, role_id: int) -> List[UserModel]:
    """
    Retrieve all users associated with a specific role from the database.

    Args:
        db (Session): The database session.
        role_id (int): The ID of the role.

    Returns:
        List[UserModel]: A list of user database objects associated with the role.

    Usage example:
        users = read_users_for_role_from_db(db, 1)
        for user in users:
            print(f"User with role 1: {user.username}")
    """
    return db.query(UserModel).filter(UserModel.role_id == role_id).all()


def read_default_role_from_db(db: Session) -> Optional[RoleModel]:
    """
    Retrieve the default role from the database.

    Args:
        db (Session): The database session.

    Returns:
        Optional[RoleModel]: The default role database object,
        or None if not found.

    Usage example:
        default_role = read_default_role_from_db(db)
        if default_role:
            print(f"Default role: {default_role.name}")
    """
    return db.query(RoleModel).filter(RoleModel.default == True).first()
