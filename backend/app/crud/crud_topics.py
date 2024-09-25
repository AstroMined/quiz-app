# filename: backend/app/crud/crud_topics.py

"""
This module handles CRUD operations for topics in the database.

It provides functions for creating, reading, updating, and deleting topics,
as well as managing associations between topics and related models such as
subjects, subtopics, and questions.

Key dependencies:
- sqlalchemy.orm: For database session management
- sqlalchemy.exc: For handling IntegrityError and SQLAlchemyError
- fastapi: For raising HTTPExceptions
- backend.app.models: For various model classes (TopicModel, SubjectModel, etc.)
- backend.app.services.logging_service: For logging

Main functions:
- create_topic_in_db: Creates a new topic
- read_topic_from_db: Retrieves a single topic by ID
- read_topic_by_name_from_db: Retrieves a single topic by name
- read_topics_from_db: Retrieves multiple topics with pagination
- update_topic_in_db: Updates an existing topic
- delete_topic_from_db: Deletes a topic
- create/delete association functions: Manage relationships between topics and other entities
- read_subjects/subtopics/questions_for_topic_from_db: Retrieve related entities for a topic

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_topics import create_topic_in_db

    def add_new_topic(db: Session, name: str, subject_ids: List[int]):
        topic_data = {"name": name, "subject_ids": subject_ids}
        return create_topic_in_db(db, topic_data)
"""

from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import (
    QuestionToTopicAssociation,
    SubjectToTopicAssociation,
    TopicToSubtopicAssociation,
)
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger


def create_topic_in_db(db: Session, topic_data: Dict) -> Optional[TopicModel]:
    """
    Create a new topic in the database.

    Args:
        db (Session): The database session.
        topic_data (Dict): A dictionary containing the topic data.
            Required keys: "name"
            Optional keys: "subject_ids", "subtopic_ids", "question_ids"

    Returns:
        Optional[TopicModel]: The created topic database object, or None if creation fails.

    Raises:
        HTTPException: If an invalid subject_id is provided.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        topic_data = {
            "name": "Algebra",
            "subject_ids": [1, 2],
            "subtopic_ids": [1, 2, 3],
            "question_ids": [1, 2, 3, 4]
        }
        new_topic = create_topic_in_db(db, topic_data)
    """
    # Validate subject IDs before creating the topic
    if "subject_ids" in topic_data and topic_data["subject_ids"]:
        for subject_id in topic_data["subject_ids"]:
            subject = (
                db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
            )
            if not subject:
                raise HTTPException(
                    status_code=400, detail=f"Invalid subject_id: {subject_id}"
                )

    db_topic = TopicModel(name=topic_data["name"])
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)

    if "subject_ids" in topic_data and topic_data["subject_ids"]:
        for subject_id in topic_data["subject_ids"]:
            create_subject_to_topic_association_in_db(db, subject_id, db_topic.id)

    if "subtopic_ids" in topic_data and topic_data["subtopic_ids"]:
        for subtopic_id in topic_data["subtopic_ids"]:
            create_topic_to_subtopic_association_in_db(db, db_topic.id, subtopic_id)

    if "question_ids" in topic_data and topic_data["question_ids"]:
        for question_id in topic_data["question_ids"]:
            create_question_to_topic_association_in_db(db, question_id, db_topic.id)

    return db_topic


def read_topic_from_db(db: Session, topic_id: int) -> Optional[TopicModel]:
    """
    Retrieve a single topic from the database by its ID.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic to retrieve.

    Returns:
        Optional[TopicModel]: The retrieved topic database object,
        or None if not found.

    Usage example:
        topic = read_topic_from_db(db, 1)
        if topic:
            print(f"Topic name: {topic.name}")
    """
    topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if topic:
        # Manually load the subjects
        topic.subjects = read_subjects_for_topic_from_db(db, topic_id)
        logger.debug("Loaded subjects for topic: %s", topic.subjects)
    return topic


def read_topic_by_name_from_db(db: Session, name: str) -> Optional[TopicModel]:
    """
    Retrieve a single topic from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the topic to retrieve.

    Returns:
        Optional[TopicModel]: The retrieved topic database object,
        or None if not found.

    Usage example:
        topic = read_topic_by_name_from_db(db, "Algebra")
        if topic:
            print(f"Topic ID: {topic.id}")
    """
    return db.query(TopicModel).filter(TopicModel.name == name).first()


def read_topics_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[TopicModel]:
    """
    Retrieve a list of topics from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[TopicModel]: A list of retrieved topic database objects.

    Usage example:
        topics = read_topics_from_db(db, skip=10, limit=20)
        for topic in topics:
            print(f"Topic: {topic.name}")
    """
    return db.query(TopicModel).offset(skip).limit(limit).all()


def update_topic_in_db(
    db: Session, topic_id: int, topic_data: Dict
) -> Optional[TopicModel]:
    """
    Update an existing topic in the database.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic to update.
        topic_data (Dict): A dictionary containing the updated topic data.
            Optional keys: "name", "subject_ids"

    Returns:
        Optional[TopicModel]: The updated topic database object,
        or None if not found or update fails.

    Raises:
        IntegrityError: If there's a database integrity issue during the update.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {
            "name": "Advanced Algebra",
            "subject_ids": [1, 2, 3]
        }
        updated_topic = update_topic_in_db(db, 1, updated_data)
        if updated_topic:
            print(f"Updated topic name: {updated_topic.name}")
    """
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        if "name" in topic_data:
            db_topic.name = topic_data["name"]

        if "subject_ids" in topic_data:
            # Remove all existing associations
            db.query(SubjectToTopicAssociation).filter(
                SubjectToTopicAssociation.topic_id == topic_id
            ).delete()

            # Create new associations
            for subject_id in topic_data["subject_ids"]:
                if (
                    not db.query(SubjectModel)
                    .filter(SubjectModel.id == subject_id)
                    .first()
                ):
                    db.rollback()
                    return None
                create_subject_to_topic_association_in_db(db, subject_id, topic_id)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(db_topic)
    return db_topic


def delete_topic_from_db(db: Session, topic_id: int) -> bool:
    """
    Delete a topic from the database.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic to delete.

    Returns:
        bool: True if the topic was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_topic_from_db(db, 1):
            print("Topic successfully deleted")
        else:
            print("Topic not found or couldn't be deleted")
    """
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        db.delete(db_topic)
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
        db.flush()
        logger.debug(
            "Created association: subject_id=%s, topic_id=%s",
            subject_id,
            topic_id
        )
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(
            "Failed to create association: subject_id=%s, topic_id=%s. Error: %s",
            subject_id,
            topic_id,
            str(e)
        )
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


def create_topic_to_subtopic_association_in_db(
    db: Session, topic_id: int, subtopic_id: int
) -> bool:
    """
    Create an association between a topic and a subtopic in the database.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic.
        subtopic_id (int): The ID of the subtopic.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_topic_to_subtopic_association_in_db(db, 1, 2):
            print("Topic-subtopic association created successfully")
        else:
            print("Failed to create topic-subtopic association")
    """
    association = TopicToSubtopicAssociation(topic_id=topic_id, subtopic_id=subtopic_id)
    db.add(association)
    try:
        db.flush()
        return True
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "Failed to create topic-subtopic association: topic_id=%s, subtopic_id=%s",
            topic_id,
            subtopic_id
        )
        return False


def delete_topic_to_subtopic_association_from_db(
    db: Session, topic_id: int, subtopic_id: int
) -> bool:
    """
    Delete an association between a topic and a subtopic from the database.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic.
        subtopic_id (int): The ID of the subtopic.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_topic_to_subtopic_association_from_db(db, 1, 2):
            print("Topic-subtopic association deleted successfully")
        else:
            print("Topic-subtopic association not found or couldn't be deleted")
    """
    association = (
        db.query(TopicToSubtopicAssociation)
        .filter_by(topic_id=topic_id, subtopic_id=subtopic_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def create_question_to_topic_association_in_db(
    db: Session, question_id: int, topic_id: int
) -> bool:
    """
    Create an association between a question and a topic in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        topic_id (int): The ID of the topic.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_to_topic_association_in_db(db, 1, 2):
            print("Question-topic association created successfully")
        else:
            print("Failed to create question-topic association")
    """
    association = QuestionToTopicAssociation(question_id=question_id, topic_id=topic_id)
    db.add(association)
    try:
        db.flush()
        return True
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "Failed to create question-topic association: question_id=%s, topic_id=%s",
            question_id,
            topic_id
        )
        return False


def delete_question_to_topic_association_from_db(
    db: Session, question_id: int, topic_id: int
) -> bool:
    """
    Delete an association between a question and a topic from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        topic_id (int): The ID of the topic.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_to_topic_association_from_db(db, 1, 2):
            print("Question-topic association deleted successfully")
        else:
            print("Question-topic association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionToTopicAssociation)
        .filter_by(question_id=question_id, topic_id=topic_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_subjects_for_topic_from_db(db: Session, topic_id: int) -> List[SubjectModel]:
    """
    Retrieve all subjects associated with a specific topic from the database.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic.

    Returns:
        List[SubjectModel]: A list of subject database objects associated with the topic.

    Usage example:
        subjects = read_subjects_for_topic_from_db(db, 1)
        for subject in subjects:
            print(f"Subject for topic 1: {subject.name}")
    """
    return (
        db.query(SubjectModel)
        .join(SubjectToTopicAssociation)
        .filter(SubjectToTopicAssociation.topic_id == topic_id)
        .all()
    )


def read_subtopics_for_topic_from_db(db: Session, topic_id: int) -> List[SubtopicModel]:
    """
    Retrieve all subtopics associated with a specific topic from the database.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic.

    Returns:
        List[SubtopicModel]: A list of subtopic database objects associated with the topic.

    Usage example:
        subtopics = read_subtopics_for_topic_from_db(db, 1)
        for subtopic in subtopics:
            print(f"Subtopic for topic 1: {subtopic.name}")
    """
    return (
        db.query(SubtopicModel)
        .join(TopicToSubtopicAssociation)
        .filter(TopicToSubtopicAssociation.topic_id == topic_id)
        .all()
    )


def read_questions_for_topic_from_db(db: Session, topic_id: int) -> List[QuestionModel]:
    """
    Retrieve all questions associated with a specific topic from the database.

    Args:
        db (Session): The database session.
        topic_id (int): The ID of the topic.

    Returns:
        List[QuestionModel]: A list of question database objects associated with the topic.

    Usage example:
        questions = read_questions_for_topic_from_db(db, 1)
        for question in questions:
            print(f"Question for topic 1: {question.text}")
    """
    return (
        db.query(QuestionModel)
        .join(QuestionToTopicAssociation)
        .filter(QuestionToTopicAssociation.topic_id == topic_id)
        .all()
    )
