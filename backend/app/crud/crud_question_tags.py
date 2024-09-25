# filename: backend/app/crud/crud_question_tags.py

"""
This module handles CRUD operations for question tags in the database.

It provides functions for creating, reading, updating, and deleting question tags,
as well as managing associations between questions and tags.

Key dependencies:
- sqlalchemy.orm: For database session management
- sqlalchemy.exc: For handling IntegrityError
- backend.app.models.associations: For QuestionToTagAssociation
- backend.app.models.question_tags: For the QuestionTagModel
- backend.app.models.questions: For the QuestionModel

Main functions:
- create_question_tag_in_db: Creates a new question tag
- read_question_tag_from_db: Retrieves a single question tag by ID
- read_question_tag_by_tag_from_db: Retrieves a single question tag by tag name
- read_question_tags_from_db: Retrieves multiple question tags with pagination
- update_question_tag_in_db: Updates an existing question tag
- delete_question_tag_from_db: Deletes a question tag
- create_question_to_tag_association_in_db: Associates a question with a tag
- delete_question_to_tag_association_from_db: Removes a question-tag association
- read_tags_for_question_from_db: Retrieves tags for a question
- read_questions_for_tag_from_db: Retrieves questions for a tag

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_question_tags import create_question_tag_in_db

    def add_new_question_tag(db: Session, tag: str, description: str):
        question_tag_data = {"tag": tag, "description": description}
        return create_question_tag_in_db(db, question_tag_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.associations import QuestionToTagAssociation
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.services.logging_service import logger


def create_question_tag_in_db(db: Session, question_tag_data: Dict) -> QuestionTagModel:
    """
    Create a new question tag in the database.

    Args:
        db (Session): The database session.
        question_tag_data (Dict): A dictionary containing the question tag data.
            Required keys: "tag"
            Optional keys: "description"

    Returns:
        QuestionTagModel: The created question tag database object.

    Raises:
        IntegrityError: If the tag already exists.
        ValueError: If the tag is None or empty.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        question_tag_data = {
            "tag": "algebra",
            "description": "Questions related to algebra"
        }
        new_tag = create_question_tag_in_db(db, question_tag_data)
    """
    # Check if the tag already exists
    existing_tag = read_question_tag_by_tag_from_db(db, question_tag_data["tag"])
    if existing_tag:
        raise IntegrityError("Tag already exists", params=question_tag_data, orig=None)
    if question_tag_data["tag"] is not None and question_tag_data["tag"] != "":
        db_question_tag = QuestionTagModel(
            tag=question_tag_data["tag"],
            description=question_tag_data.get("description"),
        )
        db.add(db_question_tag)
    else:
        raise ValueError("Tag cannot be None or empty")
    try:
        db.commit()
        db.refresh(db_question_tag)
        return db_question_tag
    except IntegrityError as e:
        logger.exception("Failed to create question tag: %s", str(e))
        db.rollback()
        raise e
    except ValueError as e:
        logger.exception("Failed to create question tag: %s", str(e))
        db.rollback()
        raise e


def read_question_tag_from_db(
    db: Session, question_tag_id: int
) -> Optional[QuestionTagModel]:
    """
    Retrieve a single question tag from the database by its ID.

    Args:
        db (Session): The database session.
        question_tag_id (int): The ID of the question tag to retrieve.

    Returns:
        Optional[QuestionTagModel]: The retrieved question tag database object,
        or None if not found.

    Usage example:
        tag = read_question_tag_from_db(db, 1)
        if tag:
            print(f"Tag: {tag.tag}")
    """
    return (
        db.query(QuestionTagModel)
        .filter(QuestionTagModel.id == question_tag_id)
        .first()
    )


def read_question_tag_by_tag_from_db(
    db: Session, tag: str
) -> Optional[QuestionTagModel]:
    """
    Retrieve a single question tag from the database by its tag name.

    Args:
        db (Session): The database session.
        tag (str): The tag name to search for.

    Returns:
        Optional[QuestionTagModel]: The retrieved question tag database object,
        or None if not found.

    Usage example:
        tag = read_question_tag_by_tag_from_db(db, "algebra")
        if tag:
            print(f"Tag ID: {tag.id}")
    """
    return (
        db.query(QuestionTagModel).filter(QuestionTagModel.tag == tag.lower()).first()
    )


def read_question_tags_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[QuestionTagModel]:
    """
    Retrieve a list of question tags from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[QuestionTagModel]: A list of retrieved question tag database objects.

    Usage example:
        tags = read_question_tags_from_db(db, skip=10, limit=20)
        for tag in tags:
            print(f"Tag: {tag.tag}")
    """
    return db.query(QuestionTagModel).offset(skip).limit(limit).all()


def update_question_tag_in_db(
    db: Session, question_tag_id: int, question_tag_data: Dict
) -> Optional[QuestionTagModel]:
    """
    Update an existing question tag in the database.

    Args:
        db (Session): The database session.
        question_tag_id (int): The ID of the question tag to update.
        question_tag_data (Dict): A dictionary containing the updated question tag data.
            Optional keys: "tag", "description"

    Returns:
        Optional[QuestionTagModel]: The updated question tag database object,
        or None if not found.

    Raises:
        IntegrityError: If the new tag already exists.
        ValueError: If the new tag is None or empty.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"tag": "advanced_algebra", "description": "Advanced algebra questions"}
        updated_tag = update_question_tag_in_db(db, 1, updated_data)
        if updated_tag:
            print(f"Updated tag: {updated_tag.tag}")
    """
    try:
        db_question_tag = read_question_tag_from_db(db, question_tag_id)
        if db_question_tag:
            for key, value in question_tag_data.items():
                if key == "tag":
                    existing_tag = read_question_tag_by_tag_from_db(db, value)
                    if existing_tag:
                        raise IntegrityError(
                            "Tag already exists", params=question_tag_data, orig=None
                        )
                    if value is not None and value != "":
                        setattr(db_question_tag, key, value)
                    else:
                        raise ValueError("Tag cannot be None or empty")
                setattr(db_question_tag, key, value)
            db.commit()
            db.refresh(db_question_tag)
        return db_question_tag
    except IntegrityError as e:
        logger.exception("Failed to update question tag: %s", str(e))
        db.rollback()
        raise e
    except ValueError as e:
        logger.exception("Failed to update question tag: %s", str(e))
        db.rollback()
        raise e


def delete_question_tag_from_db(db: Session, question_tag_id: int) -> bool:
    """
    Delete a question tag from the database.

    Args:
        db (Session): The database session.
        question_tag_id (int): The ID of the question tag to delete.

    Returns:
        bool: True if the question tag was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_tag_from_db(db, 1):
            print("Question tag successfully deleted")
        else:
            print("Question tag not found or couldn't be deleted")
    """
    db_question_tag = read_question_tag_from_db(db, question_tag_id)
    if db_question_tag:
        db.delete(db_question_tag)
        db.commit()
        return True
    return False


def create_question_to_tag_association_in_db(
    db: Session, question_id: int, tag_id: int
) -> bool:
    """
    Create an association between a question and a tag in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        tag_id (int): The ID of the tag.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_to_tag_association_in_db(db, 1, 2):
            print("Question-tag association created successfully")
        else:
            print("Failed to create question-tag association")
    """
    association = QuestionToTagAssociation(
        question_id=question_id, question_tag_id=tag_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except IntegrityError as e:
        logger.exception("Failed to create question-tag association: %s", str(e))
        db.rollback()
        raise e
    except ValueError as e:
        logger.exception("Failed to create question-tag association: %s", str(e))
        db.rollback()
        raise e


def delete_question_to_tag_association_from_db(
    db: Session, question_id: int, tag_id: int
) -> bool:
    """
    Delete an association between a question and a tag from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        tag_id (int): The ID of the tag.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_to_tag_association_from_db(db, 1, 2):
            print("Question-tag association deleted successfully")
        else:
            print("Question-tag association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionToTagAssociation)
        .filter_by(question_id=question_id, question_tag_id=tag_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_tags_for_question_from_db(
    db: Session, question_id: int
) -> List[QuestionTagModel]:
    """
    Retrieve all tags associated with a specific question from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.

    Returns:
        List[QuestionTagModel]: A list of question tag database objects
                                associated with the question.

    Usage example:
        tags = read_tags_for_question_from_db(db, 1)
        for tag in tags:
            print(f"Tag for question 1: {tag.tag}")
    """
    return (
        db.query(QuestionTagModel)
        .join(QuestionToTagAssociation)
        .filter(QuestionToTagAssociation.question_id == question_id)
        .all()
    )


def read_questions_for_tag_from_db(db: Session, tag_id: int) -> List[QuestionModel]:
    """
    Retrieve all questions associated with a specific tag from the database.

    Args:
        db (Session): The database session.
        tag_id (int): The ID of the tag.

    Returns:
        List[QuestionModel]: A list of question database objects associated with the tag.

    Usage example:
        questions = read_questions_for_tag_from_db(db, 1)
        for question in questions:
            print(f"Question with tag 1: {question.text}")
    """
    return (
        db.query(QuestionModel)
        .join(QuestionToTagAssociation)
        .filter(QuestionToTagAssociation.question_tag_id == tag_id)
        .all()
    )
