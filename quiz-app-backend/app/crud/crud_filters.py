from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models import (
    QuestionModel,
    SubjectModel,
    TopicModel,
    SubtopicModel,
    QuestionTagModel
)
from app.schemas import QuestionSchema

def filter_questions(
    db: Session,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    subtopic: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[QuestionSchema]:
    query = db.query(QuestionModel).join(SubjectModel).join(TopicModel).join(SubtopicModel).outerjoin(QuestionModel.tags)

    if subject:
        query = query.filter(func.lower(SubjectModel.name) == func.lower(subject))
    if topic:
        query = query.filter(func.lower(TopicModel.name) == func.lower(topic))
    if subtopic:
        query = query.filter(func.lower(SubtopicModel.name) == func.lower(subtopic))
    if difficulty:
        query = query.filter(func.lower(QuestionModel.difficulty) == func.lower(difficulty))
    if tags:
        query = query.filter(func.lower(QuestionTagModel.tag).in_([tag.lower() for tag in tags]))

    questions = query.all()
    if not questions:
        return []

    return [QuestionSchema(**question.__dict__) for question in questions]
