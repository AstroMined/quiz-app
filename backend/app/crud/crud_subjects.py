# filename: backend/app/crud/crud_subjects.py

"""
This module handles CRUD operations for subjects in the database.

It provides functions for creating, reading, updating, and deleting subjects,
as well as managing associations between subjects and related models such as
disciplines, topics, and questions.

Key dependencies:
- sqlalchemy.orm: For database session management
- sqlalchemy.exc: For handling IntegrityError
- fastapi: For raising HTTPExceptions
- backend.app.models: For various model classes (SubjectModel, DisciplineModel, etc.)
- backend.app.services.logging_service: For logging

Main functions:
- create_subject_in_db: Creates a new subject
- read_subject_from_db: Retrieves a single subject by ID
- read_subject_by_name_from_db: Retrieves a single subject by name
- read_subjects_from_db: Retrieves multiple subjects with pagination
- update_subject_in_db: Updates an existing subject
- delete_subject_from_db: Deletes a subject
- create/delete association functions: Manage relationships between subjects and other entities
- read_disciplines/topics/questions_for_subject_from_db: Retrieve related entities for a subject

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_subjects import create_subject_in_db

    def add_new_subject(db: Session, name: str, discipline_ids: List[int]):
        subject_data = {"name": name, "discipline_ids": discipline_ids}
        return create_subject_in_db(db, subject_data)
"""

from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import (
    DisciplineToSubjectAssociation,
    QuestionToSubjectAssociation,
    SubjectToTopicAssociation,
)
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger


def create_subject_in_db(db: Session, subject_data: Dict) -> SubjectModel:
    """
    Create a new subject in the database.

    Args:
        db (Session): The database session.
        subject_data (Dict): A dictionary containing the subject data.
            Required keys: "name"
            Optional keys: "discipline_ids", "topic_ids", "question_ids"

    Returns:
        SubjectModel: The created subject database object.

    Raises:
        HTTPException: If an invalid discipline_id is provided.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        subject_data = {
            "name": "Mathematics",
            "discipline_ids": [1, 2],
            "topic_ids": [1, 2, 3],
            "question_ids": [1, 2, 3, 4]
        }
        new_subject = create_subject_in_db(db, subject_data)
    """
    # Validate discipline IDs before creating the subject
    if "discipline_ids" in subject_data and subject_data["discipline_ids"]:
        for discipline_id in subject_data["discipline_ids"]:
            discipline = (
                db.query(DisciplineModel)
                .filter(DisciplineModel.id == discipline_id)
                .first()
            )
            if not discipline:
                raise HTTPException(
                    status_code=400, detail=f"Invalid discipline_id: {discipline_id}"
                )

    db_subject = SubjectModel(name=subject_data["name"])
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)

    if "discipline_ids" in subject_data and subject_data["discipline_ids"]:
        for discipline_id in subject_data["discipline_ids"]:
            create_discipline_to_subject_association_in_db(
                db, discipline_id, db_subject.id
            )

    if "topic_ids" in subject_data and subject_data["topic_ids"]:
        for topic_id in subject_data["topic_ids"]:
            create_subject_to_topic_association_in_db(db, db_subject.id, topic_id)

    if "question_ids" in subject_data and subject_data["question_ids"]:
        for question_id in subject_data["question_ids"]:
            create_question_to_subject_association_in_db(db, question_id, db_subject.id)

    return db_subject


def read_subject_from_db(db: Session, subject_id: int) -> Optional[SubjectModel]:
    """
    Retrieve a single subject from the database by its ID.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject to retrieve.

    Returns:
        Optional[SubjectModel]: The retrieved subject database object,
        or None if not found.

    Usage example:
        subject = read_subject_from_db(db, 1)
        if subject:
            print(f"Subject name: {subject.name}")
    """
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()


def read_subject_by_name_from_db(db: Session, name: str) -> Optional[SubjectModel]:
    """
    Retrieve a single subject from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the subject to retrieve.

    Returns:
        Optional[SubjectModel]: The retrieved subject database object,
        or None if not found.

    Usage example:
        subject = read_subject_by_name_from_db(db, "Mathematics")
        if subject:
            print(f"Subject ID: {subject.id}")
    """
    return db.query(SubjectModel).filter(SubjectModel.name == name).first()


def read_subjects_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[SubjectModel]:
    """
    Retrieve a list of subjects from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[SubjectModel]: A list of retrieved subject database objects.

    Usage example:
        subjects = read_subjects_from_db(db, skip=10, limit=20)
        for subject in subjects:
            print(f"Subject: {subject.name}")
    """
    return db.query(SubjectModel).offset(skip).limit(limit).all()


def update_subject_in_db(
    db: Session, subject_id: int, subject_data: Dict
) -> Optional[SubjectModel]:
    """
    Update an existing subject in the database.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject to update.
        subject_data (Dict): A dictionary containing the updated subject data.
            Optional keys: "name", "discipline_ids"

    Returns:
        Optional[SubjectModel]: The updated subject database object,
        or None if not found.

    Raises:
        HTTPException: If the subject is not found, if an invalid discipline_id is provided,
                       or if there's an integrity error (e.g., duplicate name).
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {
            "name": "Advanced Mathematics",
            "discipline_ids": [1, 2, 3]
        }
        updated_subject = update_subject_in_db(db, 1, updated_data)
        if updated_subject:
            print(f"Updated subject name: {updated_subject.name}")
    """
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        if "name" in subject_data:
            db_subject.name = subject_data["name"]

        if "discipline_ids" in subject_data:
            # Validate discipline IDs before updating
            for discipline_id in subject_data["discipline_ids"]:
                discipline = (
                    db.query(DisciplineModel)
                    .filter(DisciplineModel.id == discipline_id)
                    .first()
                )
                if not discipline:
                    logger.error("Discipline not found: %s", discipline_id)
                    raise HTTPException(
                        status_code=404, detail=f"Discipline not found: {discipline_id}"
                    )

            # Remove all existing associations
            db.query(DisciplineToSubjectAssociation).filter(
                DisciplineToSubjectAssociation.subject_id == subject_id
            ).delete()

            # Create new associations
            for discipline_id in subject_data["discipline_ids"]:
                create_discipline_to_subject_association_in_db(
                    db, discipline_id, subject_id
                )

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            logger.exception(
                "IntegrityError while updating subject %s: %s", subject_id, str(e)
            )
            raise HTTPException(
                status_code=400, detail="Subject with this name already exists"
            ) from e
        except SQLAlchemyError as e:
            db.rollback()
            logger.exception(
                "Unexpected error while updating subject %s: %s", subject_id, str(e)
            )
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred"
            ) from e
        db.refresh(db_subject)
    else:
        logger.error("Subject not found: %s", subject_id)
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject


def delete_subject_from_db(db: Session, subject_id: int) -> bool:
    """
    Delete a subject from the database.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject to delete.

    Returns:
        bool: True if the subject was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_subject_from_db(db, 1):
            print("Subject successfully deleted")
        else:
            print("Subject not found or couldn't be deleted")
    """
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False


def create_discipline_to_subject_association_in_db(
    db: Session, discipline_id: int, subject_id: int
) -> bool:
    """
    Create an association between a discipline and a subject in the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline.
        subject_id (int): The ID of the subject.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_discipline_to_subject_association_in_db(db, 1, 2):
            print("Discipline-subject association created successfully")
        else:
            print("Failed to create discipline-subject association")
    """
    association = DisciplineToSubjectAssociation(
        discipline_id=discipline_id, subject_id=subject_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as e:
        logger.exception("Error creating discipline-subject association: %s", str(e))
        db.rollback()
        return False


def delete_discipline_to_subject_association_from_db(
    db: Session, discipline_id: int, subject_id: int
) -> bool:
    """
    Delete an association between a discipline and a subject from the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline.
        subject_id (int): The ID of the subject.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_discipline_to_subject_association_from_db(db, 1, 2):
            print("Discipline-subject association deleted successfully")
        else:
            print("Discipline-subject association not found or couldn't be deleted")
    """
    association = (
        db.query(DisciplineToSubjectAssociation)
        .filter_by(discipline_id=discipline_id, subject_id=subject_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def create_subject_to_topic_association_in_db(
    db: Session, subject_id: int, topic_id: int
) -> bool:
    """
    Create an association between a subject and a topic in the database.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject.
        topic_id (int): The ID of the topic.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_subject_to_topic_association_in_db(db, 1, 2):
            print("Subject-topic association created successfully")
        else:
            print("Failed to create subject-topic association")
    """
    association = SubjectToTopicAssociation(subject_id=subject_id, topic_id=topic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as e:
        logger.exception("Error creating subject-topic association: %s", str(e))
        db.rollback()
        return False


def delete_subject_to_topic_association_from_db(
    db: Session, subject_id: int, topic_id: int
) -> bool:
    """
    Delete an association between a subject and a topic from the database.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject.
        topic_id (int): The ID of the topic.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_subject_to_topic_association_from_db(db, 1, 2):
            print("Subject-topic association deleted successfully")
        else:
            print("Subject-topic association not found or couldn't be deleted")
    """
    association = (
        db.query(SubjectToTopicAssociation)
        .filter_by(subject_id=subject_id, topic_id=topic_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def create_question_to_subject_association_in_db(
    db: Session, question_id: int, subject_id: int
) -> bool:
    """
    Create an association between a question and a subject in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        subject_id (int): The ID of the subject.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_to_subject_association_in_db(db, 1, 2):
            print("Question-subject association created successfully")
        else:
            print("Failed to create question-subject association")
    """
    association = QuestionToSubjectAssociation(
        question_id=question_id, subject_id=subject_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as e:
        logger.exception("Error creating question-subject association: %s", str(e))
        db.rollback()
        return False


def delete_question_to_subject_association_from_db(
    db: Session, question_id: int, subject_id: int
) -> bool:
    """
    Delete an association between a question and a subject from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        subject_id (int): The ID of the subject.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_to_subject_association_from_db(db, 1, 2):
            print("Question-subject association deleted successfully")
        else:
            print("Question-subject association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionToSubjectAssociation)
        .filter_by(question_id=question_id, subject_id=subject_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_disciplines_for_subject_from_db(
    db: Session, subject_id: int
) -> List[DisciplineModel]:
    """
    Retrieve all disciplines associated with a specific subject from the database.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject.

    Returns:
        List[DisciplineModel]: A list of discipline database objects associated with the subject.

    Usage example:
        disciplines = read_disciplines_for_subject_from_db(db, 1)
        for discipline in disciplines:
            print(f"Discipline for subject 1: {discipline.name}")
    """
    return (
        db.query(DisciplineModel)
        .join(DisciplineToSubjectAssociation)
        .filter(DisciplineToSubjectAssociation.subject_id == subject_id)
        .all()
    )


def read_topics_for_subject_from_db(db: Session, subject_id: int) -> List[TopicModel]:
    """
    Retrieve all topics associated with a specific subject from the database.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject.

    Returns:
        List[TopicModel]: A list of topic database objects associated with the subject.

    Usage example:
        topics = read_topics_for_subject_from_db(db, 1)
        for topic in topics:
            print(f"Topic for subject 1: {topic.name}")
    """
    return (
        db.query(TopicModel)
        .join(SubjectToTopicAssociation)
        .filter(SubjectToTopicAssociation.subject_id == subject_id)
        .all()
    )


def read_questions_for_subject_from_db(
    db: Session, subject_id: int
) -> List[QuestionModel]:
    """
    Retrieve all questions associated with a specific subject from the database.

    Args:
        db (Session): The database session.
        subject_id (int): The ID of the subject.

    Returns:
        List[QuestionModel]: A list of question database objects associated with the subject.

    Usage example:
        questions = read_questions_for_subject_from_db(db, 1)
        for question in questions:
            print(f"Question for subject 1: {question.text}")
    """
    return (
        db.query(QuestionModel)
        .join(QuestionToSubjectAssociation)
        .filter(QuestionToSubjectAssociation.subject_id == subject_id)
        .all()
    )
