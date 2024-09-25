# filename: backend/app/crud/crud_concepts.py

"""
This module handles CRUD operations for concepts in the database.

It provides functions for creating, reading, updating, and deleting concepts,
as well as managing associations between concepts, subtopics, and questions.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models.associations: For SubtopicToConceptAssociation and QuestionToConceptAssociation
- backend.app.models.concepts: For the ConceptModel
- backend.app.models.questions: For the QuestionModel
- backend.app.models.subtopics: For the SubtopicModel

Main functions:
- create_concept_in_db: Creates a new concept
- read_concept_from_db: Retrieves a single concept by ID
- read_concept_by_name_from_db: Retrieves a single concept by name
- read_concepts_from_db: Retrieves multiple concepts with pagination
- update_concept_in_db: Updates an existing concept
- delete_concept_from_db: Deletes a concept
- create_subtopic_to_concept_association_in_db: Associates a subtopic with a concept
- delete_subtopic_to_concept_association_from_db: Removes a subtopic-concept association
- create_question_to_concept_association_in_db: Associates a question with a concept
- delete_question_to_concept_association_from_db: Removes a question-concept association
- read_subtopics_for_concept_from_db: Retrieves subtopics for a concept
- read_questions_for_concept_from_db: Retrieves questions for a concept

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_concepts import create_concept_in_db

    def add_new_concept(db: Session, name: str, subtopic_ids: List[int], question_ids: List[int]):
        concept_data = {"name": name, "subtopic_ids": subtopic_ids, "question_ids": question_ids}
        return create_concept_in_db(db, concept_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import (
    QuestionToConceptAssociation,
    SubtopicToConceptAssociation,
)
from backend.app.models.concepts import ConceptModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.services.logging_service import logger


def create_concept_in_db(db: Session, concept_data: Dict) -> ConceptModel:
    """
    Create a new concept in the database.

    Args:
        db (Session): The database session.
        concept_data (Dict): A dictionary containing the concept data.
            Required keys: "name"
            Optional keys: "subtopic_ids", "question_ids"

    Returns:
        ConceptModel: The created concept database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        concept_data = {
            "name": "Photosynthesis",
            "subtopic_ids": [1, 2],
            "question_ids": [3, 4, 5]
        }
        new_concept = create_concept_in_db(db, concept_data)
    """
    db_concept = ConceptModel(name=concept_data["name"])
    db.add(db_concept)
    db.commit()
    db.refresh(db_concept)

    if "subtopic_ids" in concept_data and concept_data["subtopic_ids"]:
        for subtopic_id in concept_data["subtopic_ids"]:
            create_subtopic_to_concept_association_in_db(db, subtopic_id, db_concept.id)

    if "question_ids" in concept_data and concept_data["question_ids"]:
        for question_id in concept_data["question_ids"]:
            create_question_to_concept_association_in_db(db, question_id, db_concept.id)

    return db_concept


def read_concept_from_db(db: Session, concept_id: int) -> Optional[ConceptModel]:
    """
    Retrieve a single concept from the database by its ID.

    Args:
        db (Session): The database session.
        concept_id (int): The ID of the concept to retrieve.

    Returns:
        Optional[ConceptModel]: The retrieved concept database object,
        or None if not found.

    Usage example:
        concept = read_concept_from_db(db, 1)
        if concept:
            print(f"Concept name: {concept.name}")
    """
    return db.query(ConceptModel).filter(ConceptModel.id == concept_id).first()


def read_concept_by_name_from_db(db: Session, name: str) -> Optional[ConceptModel]:
    """
    Retrieve a single concept from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the concept to retrieve.

    Returns:
        Optional[ConceptModel]: The retrieved concept database object,
        or None if not found.

    Usage example:
        concept = read_concept_by_name_from_db(db, "Photosynthesis")
        if concept:
            print(f"Concept ID: {concept.id}")
    """
    return db.query(ConceptModel).filter(ConceptModel.name == name).first()


def read_concepts_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[ConceptModel]:
    """
    Retrieve a list of concepts from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[ConceptModel]: A list of retrieved concept database objects.

    Usage example:
        concepts = read_concepts_from_db(db, skip=10, limit=20)
        for concept in concepts:
            print(f"Concept: {concept.name}")
    """
    return db.query(ConceptModel).offset(skip).limit(limit).all()


def update_concept_in_db(
    db: Session, concept_id: int, concept_data: Dict
) -> Optional[ConceptModel]:
    """
    Update an existing concept in the database.

    Args:
        db (Session): The database session.
        concept_id (int): The ID of the concept to update.
        concept_data (Dict): A dictionary containing the updated concept data.

    Returns:
        Optional[ConceptModel]: The updated concept database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"name": "Updated Concept Name"}
        updated_concept = update_concept_in_db(db, 1, updated_data)
        if updated_concept:
            print(f"Updated concept name: {updated_concept.name}")
    """
    db_concept = read_concept_from_db(db, concept_id)
    if db_concept:
        for key, value in concept_data.items():
            setattr(db_concept, key, value)
        db.commit()
        db.refresh(db_concept)
    return db_concept


def delete_concept_from_db(db: Session, concept_id: int) -> bool:
    """
    Delete a concept from the database.

    Args:
        db (Session): The database session.
        concept_id (int): The ID of the concept to delete.

    Returns:
        bool: True if the concept was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_concept_from_db(db, 1):
            print("Concept successfully deleted")
        else:
            print("Concept not found or couldn't be deleted")
    """
    db_concept = read_concept_from_db(db, concept_id)
    if db_concept:
        db.delete(db_concept)
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
            print("Association created successfully")
        else:
            print("Failed to create association")
    """
    association = SubtopicToConceptAssociation(
        subtopic_id=subtopic_id, concept_id=concept_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error creating subtopic-concept association: %s", str(e))
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
            print("Association deleted successfully")
        else:
            print("Association not found or couldn't be deleted")
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


def create_question_to_concept_association_in_db(
    db: Session, question_id: int, concept_id: int
) -> bool:
    """
    Create an association between a question and a concept in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        concept_id (int): The ID of the concept.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_question_to_concept_association_in_db(db, 1, 2):
            print("Association created successfully")
        else:
            print("Failed to create association")
    """
    association = QuestionToConceptAssociation(
        question_id=question_id, concept_id=concept_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error creating question-concept association: %s", str(e))
        return False


def delete_question_to_concept_association_from_db(
    db: Session, question_id: int, concept_id: int
) -> bool:
    """
    Delete an association between a question and a concept from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.
        concept_id (int): The ID of the concept.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_to_concept_association_from_db(db, 1, 2):
            print("Association deleted successfully")
        else:
            print("Association not found or couldn't be deleted")
    """
    association = (
        db.query(QuestionToConceptAssociation)
        .filter_by(question_id=question_id, concept_id=concept_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_subtopics_for_concept_from_db(
    db: Session, concept_id: int
) -> List[SubtopicModel]:
    """
    Retrieve all subtopics associated with a specific concept from the database.

    Args:
        db (Session): The database session.
        concept_id (int): The ID of the concept.

    Returns:
        List[SubtopicModel]: A list of subtopic database objects associated with the concept.

    Usage example:
        subtopics = read_subtopics_for_concept_from_db(db, 1)
        for subtopic in subtopics:
            print(f"Subtopic for concept 1: {subtopic.name}")
    """
    return (
        db.query(SubtopicModel)
        .join(SubtopicToConceptAssociation)
        .filter(SubtopicToConceptAssociation.concept_id == concept_id)
        .all()
    )


def read_questions_for_concept_from_db(
    db: Session, concept_id: int
) -> List[QuestionModel]:
    """
    Retrieve all questions associated with a specific concept from the database.

    Args:
        db (Session): The database session.
        concept_id (int): The ID of the concept.

    Returns:
        List[QuestionModel]: A list of question database objects associated with the concept.

    Usage example:
        questions = read_questions_for_concept_from_db(db, 1)
        for question in questions:
            print(f"Question for concept 1: {question.text}")
    """
    return (
        db.query(QuestionModel)
        .join(QuestionToConceptAssociation)
        .filter(QuestionToConceptAssociation.concept_id == concept_id)
        .all()
    )
