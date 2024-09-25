# filename: backend/app/crud/crud_filters.py

"""
This module handles filtering operations for questions in the database.

It provides a function for retrieving filtered questions based on various criteria
such as subject, topic, subtopic, difficulty, and question tags.

Key dependencies:
- sqlalchemy: For database querying and filtering
- sqlalchemy.orm: For database session management and query options
- backend.app.core.config: For DifficultyLevel enum
- backend.app.models: For various model classes (QuestionModel, SubjectModel, etc.)

Main function:
- read_filtered_questions_from_db: Retrieves questions based on specified filters

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_filters import read_filtered_questions_from_db

    def get_filtered_questions(db: Session, filters: Dict):
        return read_filtered_questions_from_db(db, filters)
"""

from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def read_filtered_questions_from_db(
    db: Session, filters: Dict, skip: int = 0, limit: int = 100
) -> List[QuestionModel]:
    """
    Retrieve filtered questions from the database based on specified criteria.

    This function applies various filters to the questions in the database and returns
    a list of questions that match all the specified criteria. It supports filtering by
    subject, topic, subtopic, difficulty level, and question tags.

    Args:
        db (Session): The database session.
        filters (Dict): A dictionary containing the filter criteria.
            Possible keys:
            - "subject": str, the name of the subject (case-insensitive)
            - "topic": str, the name of the topic (case-insensitive)
            - "subtopic": str, the name of the subtopic (case-insensitive)
            - "difficulty": DifficultyLevel, the difficulty level of the questions
            - "question_tags": List[str], a list of tags to filter by (case-insensitive)
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[QuestionModel]: A list of question database objects that match the specified filters.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        filters = {
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": DifficultyLevel.MEDIUM,
            "question_tags": ["linear equations", "polynomials"]
        }
        filtered_questions = read_filtered_questions_from_db(db, filters, skip=0, limit=50)
        for question in filtered_questions:
            print(f"Question: {question.text}, Difficulty: {question.difficulty}")
    """
    query = db.query(QuestionModel).options(
        joinedload(QuestionModel.subjects),
        joinedload(QuestionModel.topics),
        joinedload(QuestionModel.subtopics),
        joinedload(QuestionModel.question_tags),
    )

    if filters.get("subject"):
        query = query.join(QuestionModel.subjects).filter(
            func.lower(SubjectModel.name) == func.lower(filters["subject"])
        )
    if filters.get("topic"):
        query = query.join(QuestionModel.topics).filter(
            func.lower(TopicModel.name) == func.lower(filters["topic"])
        )
    if filters.get("subtopic"):
        query = query.join(QuestionModel.subtopics).filter(
            func.lower(SubtopicModel.name) == func.lower(filters["subtopic"])
        )
    if filters.get("difficulty"):
        query = query.filter(QuestionModel.difficulty == filters["difficulty"])
    if filters.get("question_tags"):
        query = query.join(QuestionModel.question_tags).filter(
            QuestionTagModel.tag.in_([tag.lower() for tag in filters["question_tags"]])
        )

    return query.offset(skip).limit(limit).all()
