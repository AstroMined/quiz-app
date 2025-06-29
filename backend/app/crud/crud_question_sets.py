# filename: backend/app/crud/crud_question_sets.py

"""
This module handles CRUD operations for question sets in the database.

It provides functions for creating, reading, updating, and deleting question sets,
as well as managing associations between question sets, questions, and groups.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.crud.crud_groups: For reading group information
- backend.app.crud.crud_questions: For reading question information
- backend.app.models.associations: For QuestionSetToGroupAssociation 
                                   and QuestionSetToQuestionAssociation
- backend.app.models.groups: For the GroupModel
- backend.app.models.question_sets: For the QuestionSetModel
- backend.app.models.questions: For the QuestionModel
- backend.app.services.logging_service: For logging

Main functions:
- create_question_set_in_db: Creates a new question set
- read_question_set_from_db: Retrieves a single question set by ID
- read_question_sets_from_db: Retrieves multiple question sets with pagination
- update_question_set_in_db: Updates an existing question set
- delete_question_set_from_db: Deletes a question set
- create_question_set_to_question_association_in_db: Associates a question with a question set
- delete_question_set_to_question_association_from_db: Removes a question-question set association
- create_question_set_to_group_association_in_db: Associates a group with a question set
- delete_question_set_to_group_association_from_db: Removes a group-question set association
- read_questions_for_question_set_from_db: Retrieves questions for a question set
- read_groups_for_question_set_from_db: Retrieves groups for a question set

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_question_sets import create_question_set_in_db

    def add_new_question_set(db: Session, name: str, description: str, creator_id: int):
        question_set_data = {"name": name, "description": description, "creator_id": creator_id}
        return create_question_set_in_db(db, question_set_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.crud.crud_groups import read_group_from_db
from backend.app.crud.crud_questions import read_question_from_db
from backend.app.models.associations import (
    QuestionSetToGroupAssociation,
    QuestionSetToQuestionAssociation,
)
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.questions import QuestionModel
from backend.app.services.logging_service import logger


def check_existing_question_set(
    db: Session, name: str, creator_id: int
) -> Optional[QuestionSetModel]:
    """
    Check if a question set with the given name and creator already exists.

    Args:
        db (Session): The database session.
        name (str): The name of the question set.
        creator_id (int): The ID of the creator.

    Returns:
        Optional[QuestionSetModel]: The existing question set if found, None otherwise.

    Usage example:
        existing_set = check_existing_question_set(db, "Math Quiz", 1)
        if existing_set:
            print(f"Question set '{existing_set.name}' already exists")
    """
    return (
        db.query(QuestionSetModel)
        .filter(
            QuestionSetModel.name == name, QuestionSetModel.creator_id == creator_id
        )
        .first()
    )


def create_question_set_in_db(db: Session, question_set_data: Dict) -> QuestionSetModel:
    """
    Create a new question set in the database.

    Args:
        db (Session): The database session.
        question_set_data (Dict): A dictionary containing the question set data.
            Required keys: "name", "creator_id"
            Optional keys: "description", "is_public", "question_ids", "group_ids"

    Returns:
        QuestionSetModel: The created question set database object.

    Raises:
        ValueError: If a question set with the same name already exists for the creator,
                    or if any of the provided question_ids or group_ids don't exist.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        question_set_data = {
            "name": "Math Quiz",
            "description": "A quiz about basic math",
            "creator_id": 1,
            "is_public": True,
            "question_ids": [1, 2, 3],
            "group_ids": [1]
        }
        new_question_set = create_question_set_in_db(db, question_set_data)
    """
    existing_question_set = check_existing_question_set(
        db, question_set_data["name"], question_set_data["creator_id"]
    )
    if existing_question_set:
        raise ValueError("A question set with this name already exists for this user")

    try:
        db_question_set = QuestionSetModel(
            name=question_set_data["name"],
            description=question_set_data.get("description"),
            is_public=question_set_data.get("is_public", True),
            creator_id=question_set_data["creator_id"],
        )
        db.add(db_question_set)
        db.commit()
        db.refresh(db_question_set)

        if "question_ids" in question_set_data:
            add_questions_to_question_set(
                db, db_question_set.id, question_set_data["question_ids"]
            )

        if "group_ids" in question_set_data:
            add_groups_to_question_set(
                db, db_question_set.id, question_set_data["group_ids"]
            )

        db.commit()
        db.refresh(db_question_set)
        return db_question_set

    except ValueError as exc:
        logger.exception("Error creating question set: %s", str(exc))
        db.rollback()
        raise exc
    except SQLAlchemyError as exc:
        logger.exception("Error creating question set: %s", str(exc))
        db.rollback()
        raise


def add_questions_to_question_set(
    db: Session, question_set_id: int, question_ids: List[int]
):
    """
    Add questions to a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        question_ids (List[int]): List of question IDs to add.

    Raises:
        ValueError: If any of the provided question_ids don't exist.
    """
    for question_id in question_ids:
        question = read_question_from_db(db, question_id)
        logger.debug("question: %s", question)
        if question:
            association = QuestionSetToQuestionAssociation(
                question_set_id=question_set_id, question_id=question_id
            )
            db.add(association)
        else:
            raise ValueError(f"Question with id {question_id} does not exist")


def add_groups_to_question_set(db: Session, question_set_id: int, group_ids: List[int]):
    """
    Add groups to a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        group_ids (List[int]): List of group IDs to add.

    Raises:
        ValueError: If any of the provided group_ids don't exist.
    """
    for group_id in group_ids:
        group = read_group_from_db(db, group_id)
        if group:
            association = QuestionSetToGroupAssociation(
                question_set_id=question_set_id, group_id=group_id
            )
            db.add(association)
        else:
            raise ValueError(f"Group with id {group_id} does not exist")


def read_question_set_from_db(
    db: Session, question_set_id: int
) -> Optional[QuestionSetModel]:
    """
    Retrieve a single question set from the database by its ID.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set to retrieve.

    Returns:
        Optional[QuestionSetModel]: The retrieved question set database object,
        or None if not found.

    Usage example:
        question_set = read_question_set_from_db(db, 1)
        if question_set:
            print(f"Question set name: {question_set.name}")
    """
    return (
        db.query(QuestionSetModel)
        .filter(QuestionSetModel.id == question_set_id)
        .first()
    )


def read_question_sets_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[QuestionSetModel]:
    """
    Retrieve a list of question sets from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[QuestionSetModel]: A list of retrieved question set database objects.

    Usage example:
        question_sets = read_question_sets_from_db(db, skip=10, limit=20)
        for question_set in question_sets:
            print(f"Question set: {question_set.name}")
    """
    return db.query(QuestionSetModel).offset(skip).limit(limit).all()


def update_question_set_in_db(
    db: Session, question_set_id: int, question_set_data: Dict
) -> Optional[QuestionSetModel]:
    """
    Update an existing question set in the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set to update.
        question_set_data (Dict): A dictionary containing the updated question set data.
            Optional keys: "name", "description", "is_public", "question_ids", "group_ids"

    Returns:
        Optional[QuestionSetModel]: The updated question set database object,
        or None if not found.

    Raises:
        ValueError: If the question set doesn't exist, or if any of the provided
                    question_ids or group_ids don't exist.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {
            "name": "Updated Math Quiz",
            "question_ids": [1, 2, 3, 4],
            "group_ids": [1, 2]
        }
        updated_question_set = update_question_set_in_db(db, 1, updated_data)
        if updated_question_set:
            print(f"Updated question set name: {updated_question_set.name}")
    """
    try:
        db_question_set = read_question_set_from_db(db, question_set_id)
        if not db_question_set:
            raise ValueError(f"Question set with id {question_set_id} does not exist")

        for key, value in question_set_data.items():
            if key not in ["question_ids", "group_ids"] and value is not None:
                setattr(db_question_set, key, value)

        if "question_ids" in question_set_data and question_set_data["question_ids"] is not None:
            update_question_set_questions(
                db, question_set_id, question_set_data["question_ids"]
            )

        if "group_ids" in question_set_data and question_set_data["group_ids"] is not None:
            update_question_set_groups(
                db, question_set_id, question_set_data["group_ids"]
            )

        db.commit()
        db.refresh(db_question_set)
        return db_question_set

    except ValueError as exc:
        logger.exception("Error updating question set: %s", str(exc))
        db.rollback()
        raise exc
    except SQLAlchemyError as exc:
        logger.exception("Error updating question set: %s", str(exc))
        db.rollback()
        raise


def update_question_set_questions(
    db: Session, question_set_id: int, question_ids: List[int]
):
    """
    Update the questions associated with a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        question_ids (List[int]): List of question IDs to associate with the question set.

    Raises:
        ValueError: If any of the provided question_ids don't exist.
    """
    # Remove existing associations
    db.query(QuestionSetToQuestionAssociation).filter_by(
        question_set_id=question_set_id
    ).delete()

    # Add new associations
    add_questions_to_question_set(db, question_set_id, question_ids)


def update_question_set_groups(db: Session, question_set_id: int, group_ids: List[int]):
    """
    Update the groups associated with a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        group_ids (List[int]): List of group IDs to associate with the question set.

    Raises:
        ValueError: If any of the provided group_ids don't exist.
    """
    # Remove existing associations
    db.query(QuestionSetToGroupAssociation).filter_by(
        question_set_id=question_set_id
    ).delete()

    # Add new associations
    add_groups_to_question_set(db, question_set_id, group_ids)


def delete_question_set_from_db(db: Session, question_set_id: int) -> bool:
    """
    Delete a question set from the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set to delete.

    Returns:
        bool: True if the question set was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_set_from_db(db, 1):
            print("Question set successfully deleted")
        else:
            print("Question set not found or couldn't be deleted")
    """
    db_question_set = read_question_set_from_db(db, question_set_id)
    if db_question_set:
        db.delete(db_question_set)
        db.commit()
        return True
    return False


def create_question_set_to_question_association_in_db(
    db: Session, question_set_id: int, question_id: int
) -> bool:
    """
    Create an association between a question set and a question in the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        question_id (int): The ID of the question.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_set_to_question_association_in_db(db, 1, 2):
            print("Question added to question set successfully")
        else:
            print("Failed to add question to question set")
    """
    association = QuestionSetToQuestionAssociation(
        question_set_id=question_set_id, question_id=question_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as exc:
        logger.exception(
            "Error creating question set to question association: %s", str(exc)
        )
        db.rollback()
        return False


def delete_question_set_to_question_association_from_db(
    db: Session, question_set_id: int, question_id: int
) -> bool:
    """
    Delete an association between a question set and a question from the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.
        question_id (int): The ID of the question.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_set_to_question_association_from_db(db, 1, 2):
            print("Question removed from question set successfully")
        else:
            print("Question-question set association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionSetToQuestionAssociation)
        .filter_by(question_set_id=question_set_id, question_id=question_id)
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
    except SQLAlchemyError as exc:
        logger.exception(
            "Error creating question set to group association: %s", str(exc)
        )
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


def read_questions_for_question_set_from_db(
    db: Session, question_set_id: int
) -> List[QuestionModel]:
    """
    Retrieve all questions associated with a specific question set from the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.

    Returns:
        List[QuestionModel]: A list of question database objects associated with the question set.

    Usage example:
        questions = read_questions_for_question_set_from_db(db, 1)
        for question in questions:
            print(f"Question in set 1: {question.text}")
    """
    return (
        db.query(QuestionModel)
        .join(QuestionSetToQuestionAssociation)
        .filter(QuestionSetToQuestionAssociation.question_set_id == question_set_id)
        .all()
    )


def read_groups_for_question_set_from_db(
    db: Session, question_set_id: int
) -> List[GroupModel]:
    """
    Retrieve all groups associated with a specific question set from the database.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set.

    Returns:
        List[GroupModel]: A list of group database objects associated with the question set.

    Usage example:
        groups = read_groups_for_question_set_from_db(db, 1)
        for group in groups:
            print(f"Group for question set 1: {group.name}")
    """
    return (
        db.query(GroupModel)
        .join(QuestionSetToGroupAssociation)
        .filter(QuestionSetToGroupAssociation.question_set_id == question_set_id)
        .all()
    )
