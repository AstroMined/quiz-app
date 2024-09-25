# filename: backend/app/crud/crud_subtopics.py

"""
This module handles CRUD operations for subtopics in the database.

It provides functions for creating, reading, updating, and deleting subtopics,
as well as managing associations between subtopics and related models such as
topics, concepts, and questions.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models: For various model classes (SubtopicModel, TopicModel, etc.)

Main functions:
- create_subtopic_in_db: Creates a new subtopic
- read_subtopic_from_db: Retrieves a single subtopic by ID
- read_subtopic_by_name_from_db: Retrieves a single subtopic by name
- read_subtopics_from_db: Retrieves multiple subtopics with pagination
- update_subtopic_in_db: Updates an existing subtopic
- delete_subtopic_from_db: Deletes a subtopic
- create/delete association functions: Manage relationships between subtopics and other entities
- read_topics/concepts/questions_for_subtopic_from_db: Retrieve related entities for a subtopic

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_subtopics import create_subtopic_in_db

    def add_new_subtopic(db: Session, name: str, topic_ids: List[int]):
        subtopic_data = {"name": name, "topic_ids": topic_ids}
        return create_subtopic_in_db(db, subtopic_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import (
    QuestionToSubtopicAssociation,
    SubtopicToConceptAssociation,
    TopicToSubtopicAssociation,
)
from backend.app.models.concepts import ConceptModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger


def create_subtopic_in_db(db: Session, subtopic_data: Dict) -> SubtopicModel:
    """
    Create a new subtopic in the database.

    Args:
        db (Session): The database session.
        subtopic_data (Dict): A dictionary containing the subtopic data.
            Required keys: "name"
            Optional keys: "topic_ids", "concept_ids", "question_ids"

    Returns:
        SubtopicModel: The created subtopic database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        subtopic_data = {
            "name": "Linear Equations",
            "topic_ids": [1, 2],
            "concept_ids": [1, 2, 3],
            "question_ids": [1, 2, 3, 4]
        }
        new_subtopic = create_subtopic_in_db(db, subtopic_data)
    """
    db_subtopic = SubtopicModel(name=subtopic_data["name"])
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)

    if "topic_ids" in subtopic_data and subtopic_data["topic_ids"]:
        for topic_id in subtopic_data["topic_ids"]:
            create_topic_to_subtopic_association_in_db(db, topic_id, db_subtopic.id)

    if "concept_ids" in subtopic_data and subtopic_data["concept_ids"]:
        for concept_id in subtopic_data["concept_ids"]:
            create_subtopic_to_concept_association_in_db(db, db_subtopic.id, concept_id)

    if "question_ids" in subtopic_data and subtopic_data["question_ids"]:
        for question_id in subtopic_data["question_ids"]:
            create_question_to_subtopic_association_in_db(
                db, question_id, db_subtopic.id
            )

    return db_subtopic


def read_subtopic_from_db(db: Session, subtopic_id: int) -> Optional[SubtopicModel]:
    """
    Retrieve a single subtopic from the database by its ID.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic to retrieve.

    Returns:
        Optional[SubtopicModel]: The retrieved subtopic database object,
        or None if not found.

    Usage example:
        subtopic = read_subtopic_from_db(db, 1)
        if subtopic:
            print(f"Subtopic name: {subtopic.name}")
    """
    return db.query(SubtopicModel).filter(SubtopicModel.id == subtopic_id).first()


def read_subtopic_by_name_from_db(db: Session, name: str) -> Optional[SubtopicModel]:
    """
    Retrieve a single subtopic from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the subtopic to retrieve.

    Returns:
        Optional[SubtopicModel]: The retrieved subtopic database object,
        or None if not found.

    Usage example:
        subtopic = read_subtopic_by_name_from_db(db, "Linear Equations")
        if subtopic:
            print(f"Subtopic ID: {subtopic.id}")
    """
    return db.query(SubtopicModel).filter(SubtopicModel.name == name).first()


def read_subtopics_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[SubtopicModel]:
    """
    Retrieve a list of subtopics from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[SubtopicModel]: A list of retrieved subtopic database objects.

    Usage example:
        subtopics = read_subtopics_from_db(db, skip=10, limit=20)
        for subtopic in subtopics:
            print(f"Subtopic: {subtopic.name}")
    """
    return db.query(SubtopicModel).offset(skip).limit(limit).all()


def update_subtopic_in_db(
    db: Session, subtopic_id: int, subtopic_data: Dict
) -> Optional[SubtopicModel]:
    """
    Update an existing subtopic in the database.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic to update.
        subtopic_data (Dict): A dictionary containing the updated subtopic data.
            Optional keys: "name"

    Returns:
        Optional[SubtopicModel]: The updated subtopic database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"name": "Advanced Linear Equations"}
        updated_subtopic = update_subtopic_in_db(db, 1, updated_data)
        if updated_subtopic:
            print(f"Updated subtopic name: {updated_subtopic.name}")
    """
    db_subtopic = read_subtopic_from_db(db, subtopic_id)
    if db_subtopic:
        for key, value in subtopic_data.items():
            setattr(db_subtopic, key, value)
        db.commit()
        db.refresh(db_subtopic)
    return db_subtopic


def delete_subtopic_from_db(db: Session, subtopic_id: int) -> bool:
    """
    Delete a subtopic from the database.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic to delete.

    Returns:
        bool: True if the subtopic was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_subtopic_from_db(db, 1):
            print("Subtopic successfully deleted")
        else:
            print("Subtopic not found or couldn't be deleted")
    """
    db_subtopic = read_subtopic_from_db(db, subtopic_id)
    if db_subtopic:
        db.delete(db_subtopic)
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
        db.commit()
        return True
    except SQLAlchemyError:
        logger.exception("Failed to create topic-subtopic association")
        db.rollback()
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


def create_subtopic_to_concept_association_in_db(
    db: Session, subtopic_id: int, concept_id: int
) -> bool:
    """
    Create an association between a subtopic and a concept in the database.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic.
        concept_id (int): The ID of the concept.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_subtopic_to_concept_association_in_db(db, 1, 2):
            print("Subtopic-concept association created successfully")
        else:
            print("Failed to create subtopic-concept association")
    """
    association = SubtopicToConceptAssociation(
        subtopic_id=subtopic_id, concept_id=concept_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError:
        logger.exception("Failed to create subtopic-concept association")
        db.rollback()
        return False


def delete_subtopic_to_concept_association_from_db(
    db: Session, subtopic_id: int, concept_id: int
) -> bool:
    """
    Delete an association between a subtopic and a concept from the database.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic.
        concept_id (int): The ID of the concept.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_subtopic_to_concept_association_from_db(db, 1, 2):
            print("Subtopic-concept association deleted successfully")
        else:
            print("Subtopic-concept association not found or couldn't be deleted")
    """
    association = (
        db.query(SubtopicToConceptAssociation)
        .filter_by(subtopic_id=subtopic_id, concept_id=concept_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def create_question_to_subtopic_association_in_db(
    db: Session, question_id: int, subtopic_id: int
) -> bool:
    """
    Create an association between a question and a subtopic in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        subtopic_id (int): The ID of the subtopic.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_to_subtopic_association_in_db(db, 1, 2):
            print("Question-subtopic association created successfully")
        else:
            print("Failed to create question-subtopic association")
    """
    association = QuestionToSubtopicAssociation(
        question_id=question_id, subtopic_id=subtopic_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError:
        logger.exception("Failed to create question-subtopic association")
        db.rollback()
        return False


def delete_question_to_subtopic_association_from_db(
    db: Session, question_id: int, subtopic_id: int
) -> bool:
    """
    Delete an association between a question and a subtopic from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        subtopic_id (int): The ID of the subtopic.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_to_subtopic_association_from_db(db, 1, 2):
            print("Question-subtopic association deleted successfully")
        else:
            print("Question-subtopic association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionToSubtopicAssociation)
        .filter_by(question_id=question_id, subtopic_id=subtopic_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_topics_for_subtopic_from_db(db: Session, subtopic_id: int) -> List[TopicModel]:
    """
    Retrieve all topics associated with a specific subtopic from the database.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic.

    Returns:
        List[TopicModel]: A list of topic database objects associated with the subtopic.

    Usage example:
        topics = read_topics_for_subtopic_from_db(db, 1)
        for topic in topics:
            print(f"Topic for subtopic 1: {topic.name}")
    """
    return (
        db.query(TopicModel)
        .join(TopicToSubtopicAssociation)
        .filter(TopicToSubtopicAssociation.subtopic_id == subtopic_id)
        .all()
    )


def read_concepts_for_subtopic_from_db(
    db: Session, subtopic_id: int
) -> List[ConceptModel]:
    """
    Retrieve all concepts associated with a specific subtopic from the database.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic.

    Returns:
        List[ConceptModel]: A list of concept database objects associated with the subtopic.

    Usage example:
        concepts = read_concepts_for_subtopic_from_db(db, 1)
        for concept in concepts:
            print(f"Concept for subtopic 1: {concept.name}")
    """
    return (
        db.query(ConceptModel)
        .join(SubtopicToConceptAssociation)
        .filter(SubtopicToConceptAssociation.subtopic_id == subtopic_id)
        .all()
    )


def read_questions_for_subtopic_from_db(
    db: Session, subtopic_id: int
) -> List[QuestionModel]:
    """
    Retrieve all questions associated with a specific subtopic from the database.

    Args:
        db (Session): The database session.
        subtopic_id (int): The ID of the subtopic.

    Returns:
        List[QuestionModel]: A list of question database objects associated with the subtopic.

    Usage example:
        questions = read_questions_for_subtopic_from_db(db, 1)
        for question in questions:
            print(f"Question for subtopic 1: {question.text}")
    """
    return (
        db.query(QuestionModel)
        .join(QuestionToSubtopicAssociation)
        .filter(QuestionToSubtopicAssociation.subtopic_id == subtopic_id)
        .all()
    )
