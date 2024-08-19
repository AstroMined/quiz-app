# filename: backend/app/crud/crud_filters.py

from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def read_filtered_questions_from_db(
    db: Session,
    filters: Dict,
    skip: int = 0,
    limit: int = 100
) -> List[QuestionModel]:
    query = db.query(QuestionModel).options(
        joinedload(QuestionModel.subjects),
        joinedload(QuestionModel.topics),
        joinedload(QuestionModel.subtopics),
        joinedload(QuestionModel.question_tags)
    )

    if filters.get('subject'):
        query = query.join(QuestionModel.subjects).filter(func.lower(SubjectModel.name) == func.lower(filters['subject']))
    if filters.get('topic'):
        query = query.join(QuestionModel.topics).filter(func.lower(TopicModel.name) == func.lower(filters['topic']))
    if filters.get('subtopic'):
        query = query.join(QuestionModel.subtopics).filter(func.lower(SubtopicModel.name) == func.lower(filters['subtopic']))
    if filters.get('difficulty'):
        query = query.filter(func.lower(QuestionModel.difficulty) == func.lower(filters['difficulty']))
    if filters.get('question_tags'):
        query = query.join(QuestionModel.question_tags).filter(QuestionTagModel.tag.in_([tag.lower() for tag in filters['question_tags']]))

    return query.offset(skip).limit(limit).all()
