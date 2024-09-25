# filename: backend/app/crud/crud_questions.py
"""This module handles CRUD operations for questions in the database.

It provides functions for creating, reading, updating, and deleting questions,
as well as managing associations between questions and related models such as
answer choices, tags, sets, subjects, topics, subtopics, and concepts.

Key dependencies:
- sqlalchemy.orm: For database session management and query options
- backend.app.crud.crud_answer_choices: For answer choice related operations
- backend.app.models: For various model classes (QuestionModel, AnswerChoiceModel, etc.)
- backend.app.services.logging_service: For logging

Main functions:
- create_question_in_db: Creates a new question
- read_question_from_db: Retrieves a single question by ID
- read_questions_from_db: Retrieves multiple questions with pagination
- read_full_question_from_db: Retrieves a question with all related data
- replace_question_in_db: Replaces an existing question
- update_question_in_db: Updates an existing question
- delete_question_from_db: Deletes a question

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_questions import create_question_in_db

    def add_new_question(db: Session, text: str, difficulty: str):
        question_data = {"text": text, "difficulty": difficulty}
        return create_question_in_db(db, question_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from backend.app.crud.crud_answer_choices import (
    create_answer_choice_in_db,
    read_list_of_answer_choices_from_db,
)
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.concepts import ConceptModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger

ASSOCIATED_FIELDS = [
    "answer_choices",
    "question_tag_ids",
    "question_set_ids",
    "subject_ids",
    "topic_ids",
    "subtopic_ids",
    "answer_choice_ids",
    "concept_ids",
]


def associate_question_related_models(
    db: Session, db_question: QuestionModel, question_data: Dict
) -> None:
    """Helper function to associate related models with the question.

    Args:
        db (Session): The database session.
        db_question (QuestionModel): The question model to associate with.
        question_data (Dict): A dictionary containing the question data and related model IDs.

    This function handles the association of various related models (answer choices, tags,
    sets, etc.) with the given question. It's used internally by create_question_in_db and
    replace_question_in_db.
    """
    for key, value in question_data.items():
        if not value:
            continue

        if key in ["answer_choices", "new_answer_choices"]:
            for answer_choice_data in value:
                if (
                    "question_ids" not in answer_choice_data
                    or answer_choice_data["question_ids"] is None
                ):
                    answer_choice_data["question_ids"] = [db_question.id]
                else:
                    answer_choice_data["question_ids"].append(db_question.id)
                db_answer_choice = create_answer_choice_in_db(db, answer_choice_data)
                db_question.answer_choices.append(db_answer_choice)

        elif key == "answer_choice_ids":
            existing_answer_choices = read_list_of_answer_choices_from_db(db, value)
            db_question.answer_choices = existing_answer_choices

        elif key in [
            "question_tag_ids",
            "question_set_ids",
            "subject_ids",
            "topic_ids",
            "subtopic_ids",
            "concept_ids",
        ]:
            model_map = {
                "question_tag_ids": QuestionTagModel,
                "question_set_ids": QuestionSetModel,
                "subject_ids": SubjectModel,
                "topic_ids": TopicModel,
                "subtopic_ids": SubtopicModel,
                "concept_ids": ConceptModel,
            }
            related_items = (
                db.query(model_map[key])
                .filter(model_map[key].id.in_(value))
                .all()
            )
            current_items = getattr(db_question, key.replace("_ids", "s"))
            setattr(
                db_question,
                key.replace("_ids", "s"),
                list(set(current_items + related_items)),
            )

        else:
            setattr(db_question, key, value)


def update_associations_to_question_related_models(
    db: Session, db_question: QuestionModel, question_data: Dict
) -> None:
    """Helper function to update associations to models related to the question.

    Args:
        db (Session): The database session.
        db_question (QuestionModel): The question model to update associations for.
        question_data (Dict): A dictionary containing the updated question data and
                              related model IDs.

    This function handles updating the associations of various related models
    (answer choices, tags, sets, etc.) with the given question. It's used internally
    by update_question_in_db.
    """
    for key, value in question_data.items():
        if key not in ASSOCIATED_FIELDS or value is None:
            continue

        if key == "answer_choice_ids":
            if value:
                existing_answer_choices = (
                    db.query(AnswerChoiceModel)
                    .filter(AnswerChoiceModel.id.in_(value))
                    .all()
                )
                db_question.answer_choices = existing_answer_choices
            else:
                db_question.answer_choices = []
        elif key in [
            "question_tag_ids",
            "question_set_ids",
            "subject_ids",
            "topic_ids",
            "subtopic_ids",
            "concept_ids",
        ]:
            model_map = {
                "question_tag_ids": QuestionTagModel,
                "question_set_ids": QuestionSetModel,
                "subject_ids": SubjectModel,
                "topic_ids": TopicModel,
                "subtopic_ids": SubtopicModel,
                "concept_ids": ConceptModel,
            }
            attr_name = key.replace("_ids", "s")
            current_items = getattr(db_question, attr_name)
            if value:
                new_items = (
                    db.query(model_map[key])
                    .filter(model_map[key].id.in_(value))
                    .all()
                )
                setattr(db_question, attr_name, list(set(current_items + new_items)))
            else:
                setattr(db_question, attr_name, [])


def create_question_in_db(db: Session, question_data: Dict) -> QuestionModel:
    """Creates a new question in the database.

    Args:
        db (Session): The database session.
        question_data (Dict): A dictionary containing the question data.
            Required keys: "text", "difficulty"
            Optional keys: Various related model IDs (e.g., "answer_choice_ids",
                           "question_tag_ids", etc.)

    Returns:
        QuestionModel: The created question database object.

    Raises:
        ValueError: If the question text is None or empty.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        question_data = {
            "text": "What is 2 + 2?",
            "difficulty": "EASY",
            "answer_choices": [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True}
            ],
            "subject_ids": [1],
            "topic_ids": [2]
        }
        new_question = create_question_in_db(db, question_data)
    """
    try:
        if question_data["text"] is None or question_data["text"] == "":
            raise ValueError("Question text cannot be None or empty")
        db_question = QuestionModel(
            text=question_data["text"],
            difficulty=(
                DifficultyLevel(question_data["difficulty"])
                if isinstance(question_data["difficulty"], str)
                else question_data["difficulty"]
            ),
        )
        db.add(db_question)
        db.flush()

        # Associate related models
        associate_question_related_models(db, db_question, question_data)

        db.commit()
        db.refresh(db_question)
        return db_question

    except Exception:
        db.rollback()
        logger.exception("Error updating question")
        raise


def read_question_from_db(db: Session, question_id: int) -> Optional[QuestionModel]:
    """Retrieve a single question from the database by its ID.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to retrieve.

    Returns:
        Optional[QuestionModel]: The retrieved question database object,
        or None if not found.

    Usage example:
        question = read_question_from_db(db, 1)
        if question:
            print(f"Question text: {question.text}")
    """
    return db.query(QuestionModel).filter(QuestionModel.id == question_id).first()


def read_questions_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[QuestionModel]:
    """Retrieve a list of questions from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[QuestionModel]: A list of retrieved question database objects.

    Usage example:
        questions = read_questions_from_db(db, skip=10, limit=20)
        for question in questions:
            print(f"Question: {question.text}")
    """
    return db.query(QuestionModel).offset(skip).limit(limit).all()


def read_full_question_from_db(
    db: Session, question_id: int
) -> Optional[QuestionModel]:
    """Retrieve a single question from the database by its ID, including all related
    data.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to retrieve.

    Returns:
        Optional[QuestionModel]: The retrieved question database object with all
                                 related data loaded, or None if not found.

    Usage example:
        full_question = read_full_question_from_db(db, 1)
        if full_question:
            print(f"Question text: {full_question.text}")
            print(f"Number of answer choices: {len(full_question.answer_choices)}")
    """
    return (
        db.query(QuestionModel)
        .options(
            joinedload(QuestionModel.subjects),
            joinedload(QuestionModel.topics),
            joinedload(QuestionModel.subtopics),
            joinedload(QuestionModel.concepts),
            joinedload(QuestionModel.answer_choices),
            joinedload(QuestionModel.question_tags),
            joinedload(QuestionModel.question_sets),
            joinedload(QuestionModel.user_responses),
            joinedload(QuestionModel.creator),
        )
        .filter(QuestionModel.id == question_id)
        .first()
    )


def replace_question_in_db(
    db: Session, question_id: int, replace_data: Dict
) -> Optional[QuestionModel]:
    """Replaces an existing question in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to replace.
        replace_data (Dict): A dictionary containing the new question data.
            Required keys: "text", "difficulty"
            Optional keys: Various related model IDs (e.g., "answer_choice_ids",
                           "question_tag_ids", etc.)

    Returns:
        Optional[QuestionModel]: The updated question database object, or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        replace_data = {
            "text": "What is 3 + 3?",
            "difficulty": "MEDIUM",
            "answer_choices": [
                {"text": "5", "is_correct": False},
                {"text": "6", "is_correct": True}
            ],
            "subject_ids": [2],
            "topic_ids": [3]
        }
        updated_question = replace_question_in_db(db, 1, replace_data)
        if updated_question:
            print(f"Updated question text: {updated_question.text}")
    """
    db_question = read_question_from_db(db, question_id)
    if db_question is None:
        return None

    try:
        # Update simple fields
        for key, value in replace_data.items():
            if key not in ASSOCIATED_FIELDS and key != "new_answer_choices":
                setattr(db_question, key, value)

        # Flush changes to trigger any potential errors with simple fields
        db.flush()
        db.refresh(db_question)

        # Clear existing associations
        db_question.subjects = []
        db_question.topics = []
        db_question.subtopics = []
        db_question.concepts = []
        db_question.question_tags = []
        db_question.question_sets = []
        db_question.answer_choices = []

        # Flush changes again to trigger any potential errors with clearing associations
        db.flush()
        db.refresh(db_question)

        # Set new associations
        associate_question_related_models(db, db_question, replace_data)

        # Final flush and commit
        db.flush()
        db.commit()
        db.refresh(db_question)
        return db_question

    except Exception:
        db.rollback()
        logger.exception("Error updating question")
        raise


def update_question_in_db(
    db: Session, question_id: int, update_data: Dict
) -> Optional[QuestionModel]:
    """Updates an existing question in the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to update.
        update_data (Dict): A dictionary containing the updated question data.
            Optional keys: "text", "difficulty", various related model IDs
                           (e.g., "answer_choice_ids", "question_tag_ids", etc.)

    Returns:
        Optional[QuestionModel]: The updated question database object, or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        update_data = {
            "text": "What is 4 + 4?",
            "difficulty": "HARD",
            "answer_choice_ids": [1, 2, 3],
            "new_answer_choices": [
                {"text": "7", "is_correct": False},
                {"text": "8", "is_correct": True}
            ]
        }
        updated_question = update_question_in_db(db, 1, update_data)
        if updated_question:
            print(f"Updated question text: {updated_question.text}")
    """
    db_question = read_question_from_db(db, question_id)
    if db_question is None:
        return None

    try:
        # Handle answer choices separately
        existing_answer_choices = update_data.pop("answer_choice_ids", None)
        new_answer_choices = update_data.pop("new_answer_choices", None)

        # Update simple fields
        for key, value in update_data.items():
            if key not in ASSOCIATED_FIELDS:
                if value is not None:
                    setattr(db_question, key, value)

        # Flush changes to trigger any potential errors with simple fields
        db.flush()
        db.refresh(db_question)

        # Update associations
        update_associations_to_question_related_models(db, db_question, update_data)

        # Handle existing answer choices
        if existing_answer_choices is not None:
            db_question.answer_choices = (
                db.query(AnswerChoiceModel)
                .filter(AnswerChoiceModel.id.in_(existing_answer_choices))
                .all()
            )

        # Flush changes again to trigger any potential errors with associations
        db.flush()
        db.refresh(db_question)

        # Handle new answer choices
        if new_answer_choices:
            for answer_choice_data in new_answer_choices:
                db_answer_choice = AnswerChoiceModel(**answer_choice_data)
                db.add(db_answer_choice)
                db_question.answer_choices.append(db_answer_choice)

        # Final flush and commit
        db.flush()
        db.commit()
        db.refresh(db_question)
        return db_question

    except Exception:
        db.rollback()
        logger.exception("Error updating question")
        raise


def delete_question_from_db(db: Session, question_id: int) -> bool:
    """Delete a question from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to delete.

    Returns:
        bool: True if the question was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_question_from_db(db, 1):
            print("Question successfully deleted")
        else:
            print("Question not found or couldn't be deleted")
    """
    db_question = read_question_from_db(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False
