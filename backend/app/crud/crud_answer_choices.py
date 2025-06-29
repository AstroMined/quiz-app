# filename: backend/app/crud/crud_answer_choices.py

"""
This module handles CRUD operations for answer choices in the database.

It provides functions for creating, reading, updating, and deleting answer choices,
as well as managing associations between questions and answer choices.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models.answer_choices: For the AnswerChoiceModel
- backend.app.models.associations: For the QuestionToAnswerAssociation
- backend.app.models.questions: For the QuestionModel
- backend.app.services.logging_service: For logging

Main functions:
- create_answer_choice_in_db: Creates a new answer choice
- read_answer_choice_from_db: Retrieves a single answer choice
- read_list_of_answer_choices_from_db: Retrieves multiple answer choices
- update_answer_choice_in_db: Updates an existing answer choice
- delete_answer_choice_from_db: Deletes an answer choice
- create_question_to_answer_association_in_db: Associates a question with an answer choice
- delete_question_to_answer_association_from_db: Removes an association
- read_answer_choices_for_question_from_db: Retrieves answer choices for a question
- read_questions_for_answer_choice_from_db: Retrieves questions for an answer choice

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_answer_choices import create_answer_choice_in_db

    def add_new_answer_choice(db: Session, text: str, is_correct: bool):
        answer_choice_data = {"text": text, "is_correct": is_correct}
        return create_answer_choice_in_db(db, answer_choice_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import QuestionToAnswerAssociation
from backend.app.models.questions import QuestionModel


def create_answer_choice_in_db(
    db: Session, answer_choice_data: Dict
) -> AnswerChoiceModel:
    """
    Create a new answer choice in the database.

    Args:
        db (Session): The database session.
        answer_choice_data (Dict): A dictionary containing the answer choice data.
            Required keys: "text", "is_correct"
            Optional keys: "explanation", "question_ids"

    Returns:
        AnswerChoiceModel: The created answer choice database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        answer_choice_data = {
            "text": "Paris",
            "is_correct": True,
            "explanation": "Paris is the capital of France",
            "question_ids": [1, 2, 3]
        }
        new_answer_choice = create_answer_choice_in_db(db, answer_choice_data)
    """
    db_answer_choice = AnswerChoiceModel(
        text=answer_choice_data["text"],
        is_correct=answer_choice_data["is_correct"],
        explanation=answer_choice_data.get("explanation"),
    )
    db.add(db_answer_choice)
    db.flush()  # This assigns an ID without committing

    has_question_ids = (
        "question_ids" in answer_choice_data and answer_choice_data["question_ids"]
    )

    if has_question_ids:
        # Don't commit here, let the caller handle associations and commit
        return db_answer_choice

    # If there are no question_ids, we can commit immediately
    db.commit()
    db.refresh(db_answer_choice)
    return db_answer_choice


def read_answer_choice_from_db(
    db: Session, answer_choice_id: int
) -> Optional[AnswerChoiceModel]:
    """
    Retrieve a single answer choice from the database by its ID.

    Args:
        db (Session): The database session.
        answer_choice_id (int): The ID of the answer choice to retrieve.

    Returns:
        Optional[AnswerChoiceModel]: The retrieved answer choice database object,
        or None if not found.

    Usage example:
        answer_choice = read_answer_choice_from_db(db, 1)
        if answer_choice:
            print(f"Answer choice text: {answer_choice.text}")
    """
    return (
        db.query(AnswerChoiceModel)
        .filter(AnswerChoiceModel.id == answer_choice_id)
        .first()
    )


def read_list_of_answer_choices_from_db(
    db: Session, answer_choice_ids: List[int]
) -> List[AnswerChoiceModel]:
    """
    Retrieve multiple answer choices from the database by their IDs.

    Args:
        db (Session): The database session.
        answer_choice_ids (List[int]): A list of answer choice IDs to retrieve.

    Returns:
        List[AnswerChoiceModel]: A list of retrieved answer choice database objects.

    Usage example:
        answer_choices = read_list_of_answer_choices_from_db(db, [1, 2, 3])
        for choice in answer_choices:
            print(f"Answer choice: {choice.text}, Correct: {choice.is_correct}")
    """
    return (
        db.query(AnswerChoiceModel)
        .filter(AnswerChoiceModel.id.in_(answer_choice_ids))
        .all()
    )


def read_answer_choices_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[AnswerChoiceModel]:
    """
    Retrieve a list of answer choices from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[AnswerChoiceModel]: A list of retrieved answer choice database objects.

    Usage example:
        answer_choices = read_answer_choices_from_db(db, skip=10, limit=20)
        for choice in answer_choices:
            print(f"Answer choice: {choice.text}")
    """
    return db.query(AnswerChoiceModel).offset(skip).limit(limit).all()


def update_answer_choice_in_db(
    db: Session, answer_choice_id: int, answer_choice_data: Dict
) -> Optional[AnswerChoiceModel]:
    """
    Update an existing answer choice in the database.

    Args:
        db (Session): The database session.
        answer_choice_id (int): The ID of the answer choice to update.
        answer_choice_data (Dict): A dictionary containing the updated answer choice data.

    Returns:
        Optional[AnswerChoiceModel]: The updated answer choice database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"text": "Updated answer", "is_correct": False}
        updated_choice = update_answer_choice_in_db(db, 1, updated_data)
        if updated_choice:
            print(f"Updated answer choice: {updated_choice.text}")
    """
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id)
    if db_answer_choice:
        for key, value in answer_choice_data.items():
            setattr(db_answer_choice, key, value)
        db.commit()
        db.refresh(db_answer_choice)
    return db_answer_choice


def delete_answer_choice_from_db(db: Session, answer_choice_id: int) -> bool:
    """
    Delete an answer choice from the database.

    Args:
        db (Session): The database session.
        answer_choice_id (int): The ID of the answer choice to delete.

    Returns:
        bool: True if the answer choice was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_answer_choice_from_db(db, 1):
            print("Answer choice successfully deleted")
        else:
            print("Answer choice not found or couldn't be deleted")
    """
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id)
    if db_answer_choice:
        db.delete(db_answer_choice)
        db.commit()
        return True
    return False


def create_question_to_answer_association_in_db(
    db: Session, question_id: int, answer_choice_id: int
) -> bool:
    """
    Create an association between a question and an answer choice in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        answer_choice_id (int): The ID of the answer choice.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_to_answer_association_in_db(db, 1, 2):
            print("Association created successfully")
        else:
            print("Failed to create association")
    """
    association = QuestionToAnswerAssociation(
        question_id=question_id, answer_choice_id=answer_choice_id
    )
    db.add(association)
    try:
        db.flush()  # Changed from db.commit() to db.flush()
        return True
    except Exception as e:
        db.rollback()
        raise e


def delete_question_to_answer_association_from_db(
    db: Session, question_id: int, answer_choice_id: int
) -> bool:
    """
    Delete an association between a question and an answer choice from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        answer_choice_id (int): The ID of the answer choice.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_to_answer_association_from_db(db, 1, 2):
            print("Association deleted successfully")
        else:
            print("Association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionToAnswerAssociation)
        .filter_by(question_id=question_id, answer_choice_id=answer_choice_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_answer_choices_for_question_from_db(
    db: Session, question_id: int
) -> List[AnswerChoiceModel]:
    """
    Retrieve all answer choices associated with a specific question from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.

    Returns:
        List[AnswerChoiceModel]: A list of answer choice database objects
                                 associated with the question.

    Usage example:
        answer_choices = read_answer_choices_for_question_from_db(db, 1)
        for choice in answer_choices:
            print(f"Answer choice for question 1: {choice.text}")
    """
    return (
        db.query(AnswerChoiceModel)
        .join(QuestionToAnswerAssociation)
        .filter(QuestionToAnswerAssociation.question_id == question_id)
        .all()
    )


def read_questions_for_answer_choice_from_db(
    db: Session, answer_choice_id: int
) -> List[QuestionModel]:
    """
    Retrieve all questions associated with a specific answer choice from the database.

    Args:
        db (Session): The database session.
        answer_choice_id (int): The ID of the answer choice.

    Returns:
        List[QuestionModel]: A list of question database objects associated with the answer choice.

    Usage example:
        questions = read_questions_for_answer_choice_from_db(db, 1)
        for question in questions:
            print(f"Question for answer choice 1: {question.text}")
    """
    return (
        db.query(QuestionModel)
        .join(QuestionToAnswerAssociation)
        .filter(QuestionToAnswerAssociation.answer_choice_id == answer_choice_id)
        .all()
    )
