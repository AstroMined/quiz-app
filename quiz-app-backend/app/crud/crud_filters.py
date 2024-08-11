# filename: app/crud/crud_filters.py

from typing import List, Dict
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.models.questions import QuestionModel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.question_tags import QuestionTagModel

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
