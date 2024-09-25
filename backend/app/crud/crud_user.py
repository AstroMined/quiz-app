# filename: backend/app/crud/crud_user.py

"""
This module handles CRUD operations for users in the database.

It provides functions for creating, reading, updating, and deleting users,
as well as managing associations between users and groups, roles, and question sets.

Key dependencies:
- sqlalchemy.orm: For database session management
- sqlalchemy.exc: For handling IntegrityError
- backend.app.core.security: For password hashing
- backend.app.models: For various model classes (UserModel, GroupModel, etc.)
- backend.app.services.logging_service: For logging

Main functions:
- create_user_in_db: Creates a new user
- read_user_from_db: Retrieves a single user by ID
- read_user_by_username_from_db: Retrieves a single user by username
- read_user_by_email_from_db: Retrieves a single user by email
- read_users_from_db: Retrieves multiple users with pagination
- update_user_in_db: Updates an existing user
- delete_user_from_db: Deletes a user
- create/delete_user_to_group_association_in_db: Manages user-group associations
- read_groups_for_user_from_db: Retrieves groups for a user
- read_role_for_user_from_db: Retrieves the role for a user
- read_created_question_sets_for_user_from_db: Retrieves question sets created by a user
- update_user_token_blacklist_date: Updates the token blacklist date for a user

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_user import create_user_in_db

    def add_new_user(db: Session, username: str, email: str, password: str):
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": get_password_hash(password)
        }
        return create_user_in_db(db, user_data)
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import logger


def create_user_in_db(db: Session, user_data: Dict) -> UserModel:
    """
    Create a new user in the database.

    Args:
        db (Session): The database session.
        user_data (Dict): A dictionary containing the user data.
            Required keys: "username", "email", "hashed_password"
            Optional keys: "is_active", "is_admin", "role_id"

    Returns:
        UserModel: The created user database object.

    Raises:
        ValueError: If there's an issue with user creation (e.g.,
                    duplicate username/email, invalid role).
        Exception: For any other unexpected errors during user creation.

    Usage example:
        user_data = {
            "username": "john_doe",
            "email": "john@example.com",
            "hashed_password": "hashed_password_here",
            "role_id": 1
        }
        new_user = create_user_in_db(db, user_data)
    """
    db_user = UserModel(
        username=user_data["username"].lower(),  # Store username in lowercase
        email=user_data["email"],
        hashed_password=user_data["hashed_password"],
        is_active=user_data.get("is_active", True),
        is_admin=user_data.get("is_admin", False),
        role_id=user_data.get("role_id"),
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as exc:
        db.rollback()
        error_info = str(exc.orig)
        if "role_id" in error_info:
            raise ValueError("Role is required for user creation") from exc
        if "username" in error_info:
            raise ValueError("Username already exists") from exc
        if "email" in error_info:
            raise ValueError("Email already exists") from exc
        raise ValueError("Username or email already exists") from exc
    except Exception as exc:
        logger.exception("Error creating user: %s", exc)
        db.rollback()
        raise ValueError(f"Error creating user: {str(exc)}") from exc


def read_user_from_db(db: Session, user_id: int) -> Optional[UserModel]:
    """
    Retrieve a single user from the database by their ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to retrieve.

    Returns:
        Optional[UserModel]: The retrieved user database object, or None if not found.

    Usage example:
        user = read_user_from_db(db, 1)
        if user:
            print(f"User: {user.username}")
    """
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def read_user_by_username_from_db(db: Session, username: str) -> Optional[UserModel]:
    """
    Retrieve a single user from the database by their username.

    Args:
        db (Session): The database session.
        username (str): The username of the user to retrieve.

    Returns:
        Optional[UserModel]: The retrieved user database object, or None if not found.

    Usage example:
        user = read_user_by_username_from_db(db, "john_doe")
        if user:
            print(f"User ID: {user.id}")
    """
    user = (
        db.query(UserModel)
        .filter(func.lower(UserModel.username) == username.lower())
        .first()
    )
    if user and user.token_blacklist_date:
        # Ensure token_blacklist_date is timezone-aware
        if user.token_blacklist_date.tzinfo is None:
            user.token_blacklist_date = user.token_blacklist_date.replace(
                tzinfo=timezone.utc
            )
    return user


def read_user_by_email_from_db(db: Session, email: str) -> Optional[UserModel]:
    """
    Retrieve a single user from the database by their email.

    Args:
        db (Session): The database session.
        email (str): The email of the user to retrieve.

    Returns:
        Optional[UserModel]: The retrieved user database object, or None if not found.

    Usage example:
        user = read_user_by_email_from_db(db, "john@example.com")
        if user:
            print(f"User: {user.username}")
    """
    return db.query(UserModel).filter(UserModel.email == email).first()


def read_users_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    """
    Retrieve a list of users from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[UserModel]: A list of retrieved user database objects.

    Usage example:
        users = read_users_from_db(db, skip=10, limit=20)
        for user in users:
            print(f"User: {user.username}")
    """
    return db.query(UserModel).offset(skip).limit(limit).all()


def update_user_in_db(
    db: Session, user_id: int, user_data: Dict
) -> Optional[UserModel]:
    """
    Update an existing user in the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to update.
        user_data (Dict): A dictionary containing the updated user data.
            Possible keys: "username", "email", "password", "is_active", "is_admin", "role_id"

    Returns:
        Optional[UserModel]: The updated user database object, or None if not found.

    Raises:
        ValueError: If there's an issue with user update (e.g.,
                    duplicate username/email, invalid role).

    Usage example:
        updated_data = {"username": "new_username", "is_admin": True}
        updated_user = update_user_in_db(db, 1, updated_data)
        if updated_user:
            print(f"Updated user: {updated_user.username}")
    """
    db_user = read_user_from_db(db, user_id)
    if db_user:
        try:
            for key, value in user_data.items():
                if key == "password":
                    db_user.hashed_password = get_password_hash(value)
                elif key == "role_id":
                    role = db.query(RoleModel).filter(RoleModel.id == value).first()
                    if not role:
                        raise ValueError("Invalid role_id")
                    db_user.role_id = value
                elif key == "username":
                    db_user.username = (
                        value.lower()
                    )  # Store username in lowercase when updating
                else:
                    setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as exc:
            db.rollback()
            error_info = str(exc.orig)
            if "username" in error_info:
                raise ValueError("Username already exists") from exc
            if "email" in error_info:
                raise ValueError("Email already exists") from exc
            raise ValueError("Error updating user") from exc
        except ValueError:
            db.rollback()
            raise
    return None


def delete_user_from_db(db: Session, user_id: int) -> bool:
    """
    Delete a user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to delete.

    Returns:
        bool: True if the user was successfully deleted, False otherwise.

    Usage example:
        if delete_user_from_db(db, 1):
            print("User successfully deleted")
        else:
            print("User not found or couldn't be deleted")
    """
    db_user = read_user_from_db(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def create_user_to_group_association_in_db(
    db: Session, user_id: int, group_id: int
) -> bool:
    """
    Create an association between a user and a group in the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        group_id (int): The ID of the group.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Usage example:
        if create_user_to_group_association_in_db(db, 1, 2):
            print("User-group association created successfully")
        else:
            print("Failed to create user-group association")
    """
    association = UserToGroupAssociation(user_id=user_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def delete_user_to_group_association_from_db(
    db: Session, user_id: int, group_id: int
) -> bool:
    """
    Delete an association between a user and a group from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        group_id (int): The ID of the group.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Usage example:
        if delete_user_to_group_association_from_db(db, 1, 2):
            print("User-group association deleted successfully")
        else:
            print("User-group association not found or couldn't be deleted")
    """
    association = (
        db.query(UserToGroupAssociation)
        .filter_by(user_id=user_id, group_id=group_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_groups_for_user_from_db(db: Session, user_id: int) -> List[GroupModel]:
    """
    Retrieve all groups associated with a specific user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[GroupModel]: A list of group database objects associated with the user.

    Usage example:
        groups = read_groups_for_user_from_db(db, 1)
        for group in groups:
            print(f"Group: {group.name}")
    """
    return (
        db.query(GroupModel)
        .join(UserToGroupAssociation)
        .filter(UserToGroupAssociation.user_id == user_id)
        .all()
    )


def read_role_for_user_from_db(db: Session, user_id: int) -> Optional[RoleModel]:
    """
    Retrieve the role associated with a specific user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        Optional[RoleModel]: The role database object associated with
                             the user, or None if not found.

    Usage example:
        role = read_role_for_user_from_db(db, 1)
        if role:
            print(f"User's role: {role.name}")
    """
    user = read_user_from_db(db, user_id)
    return user.role if user else None


def read_created_question_sets_for_user_from_db(
    db: Session, user_id: int
) -> List[QuestionSetModel]:
    """
    Retrieve all question sets created by a specific user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[QuestionSetModel]: A list of question set database objects created by the user.

    Usage example:
        question_sets = read_created_question_sets_for_user_from_db(db, 1)
        for question_set in question_sets:
            print(f"Question set: {question_set.name}")
    """
    return (
        db.query(QuestionSetModel).filter(QuestionSetModel.creator_id == user_id).all()
    )


def update_user_token_blacklist_date(
    db: Session, user_id: int, new_date: Optional[datetime]
) -> Optional[UserModel]:
    """
    Update the token blacklist date for a user in the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        new_date (Optional[datetime]): The new token blacklist date.
                                       If None, it clears the existing date.

    Returns:
        Optional[UserModel]: The updated user database object, or None if the user is not found.

    Usage example:
        updated_user = update_user_token_blacklist_date(db, 1, datetime.now(timezone.utc))
        if updated_user:
            print(f"Updated token blacklist date: {updated_user.token_blacklist_date}")
    """
    db_user = read_user_from_db(db, user_id)
    if db_user:
        if new_date is not None and new_date.tzinfo is None:
            new_date = new_date.replace(tzinfo=timezone.utc)
        db_user.token_blacklist_date = new_date
        db.commit()
        db.refresh(db_user)
        return db_user
    return None
