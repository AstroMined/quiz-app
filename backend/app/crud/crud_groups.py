# filename: backend/app/crud/crud_groups.py

"""
This module handles CRUD operations for groups in the database.

It provides functions for creating, reading, updating, and deleting groups,
as well as managing associations between groups, users, and question sets.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models.associations: For UserToGroupAssociation and QuestionSetToGroupAssociation
- backend.app.models.groups: For the GroupModel
- backend.app.models.question_sets: For the QuestionSetModel
- backend.app.models.users: For the UserModel

Main functions:
- create_group_in_db: Creates a new group
- read_group_from_db: Retrieves a single group by ID
- read_groups_from_db: Retrieves multiple groups with pagination
- update_group_in_db: Updates an existing group
- delete_group_from_db: Deletes a group
- create_user_to_group_association_in_db: Associates a user with a group
- delete_user_to_group_association_from_db: Removes a user-group association
- create_question_set_to_group_association_in_db: Associates a question set with a group
- delete_question_set_to_group_association_from_db: Removes a question set-group association
- read_users_for_group_from_db: Retrieves users for a group
- read_question_sets_for_group_from_db: Retrieves question sets for a group

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_groups import create_group_in_db

    def add_new_group(db: Session, name: str, description: str, creator_id: int):
        group_data = {"name": name, "description": description, "creator_id": creator_id}
        return create_group_in_db(db, group_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import (
    QuestionSetToGroupAssociation,
    UserToGroupAssociation,
)
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import logger


def create_group_in_db(db: Session, group_data: Dict) -> GroupModel:
    """
    Create a new group in the database.

    Args:
        db (Session): The database session.
        group_data (Dict): A dictionary containing the group data.
            Required keys: "name", "creator_id"
            Optional keys: "description", "is_active"

    Returns:
        GroupModel: The created group database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        group_data = {
            "name": "Math Study Group",
            "description": "A group for studying mathematics",
            "creator_id": 1,
            "is_active": True
        }
        new_group = create_group_in_db(db, group_data)
    """
    db_group = GroupModel(
        name=group_data["name"],
        description=group_data.get("description"),
        creator_id=group_data["creator_id"],
        is_active=group_data.get("is_active", True),
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def read_group_from_db(db: Session, group_id: int) -> Optional[GroupModel]:
    """
    Retrieve a single group from the database by its ID.

    Args:
        db (Session): The database session.
        group_id (int): The ID of the group to retrieve.

    Returns:
        Optional[GroupModel]: The retrieved group database object,
        or None if not found.

    Usage example:
        group = read_group_from_db(db, 1)
        if group:
            print(f"Group name: {group.name}")
    """
    return db.query(GroupModel).filter(GroupModel.id == group_id).first()


def read_groups_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[GroupModel]:
    """
    Retrieve a list of groups from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[GroupModel]: A list of retrieved group database objects.

    Usage example:
        groups = read_groups_from_db(db, skip=10, limit=20)
        for group in groups:
            print(f"Group: {group.name}")
    """
    return db.query(GroupModel).offset(skip).limit(limit).all()


def update_group_in_db(
    db: Session, group_id: int, group_data: Dict
) -> Optional[GroupModel]:
    """
    Update an existing group in the database.

    Args:
        db (Session): The database session.
        group_id (int): The ID of the group to update.
        group_data (Dict): A dictionary containing the updated group data.

    Returns:
        Optional[GroupModel]: The updated group database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"name": "Updated Group Name", "is_active": False}
        updated_group = update_group_in_db(db, 1, updated_data)
        if updated_group:
            print(f"Updated group name: {updated_group.name}")
    """
    db_group = read_group_from_db(db, group_id)
    if db_group:
        for key, value in group_data.items():
            setattr(db_group, key, value)
        db.commit()
        db.refresh(db_group)
    return db_group


def delete_group_from_db(db: Session, group_id: int) -> bool:
    """
    Delete a group from the database.

    Args:
        db (Session): The database session.
        group_id (int): The ID of the group to delete.

    Returns:
        bool: True if the group was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_group_from_db(db, 1):
            print("Group successfully deleted")
        else:
            print("Group not found or couldn't be deleted")
    """
    db_group = read_group_from_db(db, group_id)
    if db_group:
        db.delete(db_group)
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

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_user_to_group_association_in_db(db, 1, 2):
            print("User added to group successfully")
        else:
            print("Failed to add user to group")
    """
    association = UserToGroupAssociation(user_id=user_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError:
        logger.exception("Failed to create user-group association")
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

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_user_to_group_association_from_db(db, 1, 2):
            print("User removed from group successfully")
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


def create_question_set_to_group_association_in_db(
    db: Session, question_set_id: int, group_id: int
) -> bool:
    """
    Create an association between a question set and a group in the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        group_id (int): The ID of the group.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_set_to_group_association_in_db(db, 1, 2):
            print("Question set added to group successfully")
        else:
            print("Failed to add question set to group")
    """
    association = QuestionSetToGroupAssociation(
        question_set_id=question_set_id, group_id=group_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError:
        logger.exception("Failed to create question set-group association")
        db.rollback()
        return False


def delete_question_set_to_group_association_from_db(
    db: Session, question_set_id: int, group_id: int
) -> bool:
    """
    Delete an association between a question set and a group from the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        group_id (int): The ID of the group.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_set_to_group_association_from_db(db, 1, 2):
            print("Question set removed from group successfully")
        else:
            print("Question set-group association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionSetToGroupAssociation)
        .filter_by(question_set_id=question_set_id, group_id=group_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_users_for_group_from_db(db: Session, group_id: int) -> List[UserModel]:
    """
    Retrieve all users associated with a specific group from the database.

    Args:
        db (Session): The database session.
        group_id (int): The ID of the group.

    Returns:
        List[UserModel]: A list of user database objects associated with the group.

    Usage example:
        users = read_users_for_group_from_db(db, 1)
        for user in users:
            print(f"User in group 1: {user.username}")
    """
    return (
        db.query(UserModel)
        .join(UserToGroupAssociation)
        .filter(UserToGroupAssociation.group_id == group_id)
        .all()
    )


def read_question_sets_for_group_from_db(
    db: Session, group_id: int
) -> List[QuestionSetModel]:
    """
    Retrieve all question sets associated with a specific group from the database.

    Args:
        db (Session): The database session.
        group_id (int): The ID of the group.

    Returns:
        List[QuestionSetModel]: A list of question set database objects associated with the group.

    Usage example:
        question_sets = read_question_sets_for_group_from_db(db, 1)
        for question_set in question_sets:
            print(f"Question set for group 1: {question_set.name}")
    """
    return (
        db.query(QuestionSetModel)
        .join(QuestionSetToGroupAssociation)
        .filter(QuestionSetToGroupAssociation.group_id == group_id)
        .all()
    )
