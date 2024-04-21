# filename: app/crud/crud_filters.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import (
    QuestionModel,
    SubjectModel,
    TopicModel,
    SubtopicModel,
    QuestionTagModel
)
from app.schemas import QuestionSchema, FilterParamsSchema

def filter_questions(
    db: Session,
    filters: FilterParamsSchema,
    skip: int = 0,
    limit: int = 100
) -> Optional[List[QuestionSchema]]:
    query = db.query(QuestionModel).join(SubjectModel).join(TopicModel).join(SubtopicModel).outerjoin(QuestionModel.tags)

    if filters.subject:
        query = query.filter(func.lower(SubjectModel.name) == func.lower(filters.subject))
    if filters.topic:
        query = query.filter(func.lower(TopicModel.name) == func.lower(filters.topic))
    if filters.subtopic:
        query = query.filter(func.lower(SubtopicModel.name) == func.lower(filters.subtopic))
    if filters.difficulty:
        query = query.filter(func.lower(QuestionModel.difficulty) == func.lower(filters.difficulty))
    if filters.tags:
        query = query.filter(func.lower(QuestionTagModel.tag).in_([tag.lower() for tag in filters.tags]))

    questions = query.offset(skip).limit(limit).all()

    if not questions:
        return []

    return [QuestionSchema.model_validate(question) for question in questions]
