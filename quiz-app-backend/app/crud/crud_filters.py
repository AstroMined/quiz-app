# filename: app/crud/crud_filters.py

from typing import List, Optional
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.questions import QuestionModel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.question_tags import QuestionTagModel
from app.schemas.questions import QuestionSchema
from app.schemas.filters import FilterParamsSchema

def filter_questions_crud(
    db: Session,
    filters: dict,  # Change this parameter to expect a dictionary
    skip: int = 0,
    limit: int = 100
) -> Optional[List[QuestionSchema]]:
    print("Entering filter_questions function")
    print(f"Received filters: {filters}")
    try:
        # Validate filters dictionary against the Pydantic model
        validated_filters = FilterParamsSchema(**filters)
    except ValidationError as e:
        print(f"Invalid filters: {str(e)}")
        raise e

    if not any(value for value in filters.values()):
        print("No filters provided")
        return None

    query = db.query(QuestionModel).join(SubjectModel).join(TopicModel).join(SubtopicModel).outerjoin(QuestionModel.tags)

    if validated_filters.subject:
        query = query.filter(func.lower(SubjectModel.name) == func.lower(validated_filters.subject))
    if validated_filters.topic:
        query = query.filter(func.lower(TopicModel.name) == func.lower(validated_filters.topic))
    if validated_filters.subtopic:
        query = query.filter(func.lower(SubtopicModel.name) == func.lower(validated_filters.subtopic))
    if validated_filters.difficulty:
        query = query.filter(func.lower(QuestionModel.difficulty) == func.lower(validated_filters.difficulty))
    if validated_filters.tags:
        query = query.filter(QuestionTagModel.tag.in_([tag.lower() for tag in validated_filters.tags]))

    questions = query.offset(skip).limit(limit).all()

    print("Returning filtered questions")
    return [QuestionSchema.model_validate(question) for question in questions]
