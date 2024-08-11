# filename: app/crud/crud_questions.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.questions import QuestionModel, DifficultyLevel
from app.models.answer_choices import AnswerChoiceModel
from app.models.question_tags import QuestionTagModel
from app.models.question_sets import QuestionSetModel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.concepts import ConceptModel

def associate_related_models(db: Session, db_question: QuestionModel, question_data: Dict) -> None:
    """Helper function to associate related models with the question."""

    # Iterate over keys
    for key, value in question_data.items():
        if not value:
            continue

        if key == 'answer_choices':
            for answer_choice_data in value:
                db_answer_choice = AnswerChoiceModel(**answer_choice_data)
                db.add(db_answer_choice)
                db_question.answer_choices.append(db_answer_choice)

        elif key == 'answer_choice_ids':
            existing_answer_choices = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id.in_(value)).all()
            db_question.answer_choices = existing_answer_choices

        elif key in ['question_tag_ids', 'question_set_ids', 'subject_ids', 'topic_ids', 'subtopic_ids', 'concept_ids']:
            model_map = {
                'question_tag_ids': QuestionTagModel,
                'question_set_ids': QuestionSetModel,
                'subject_ids': SubjectModel,
                'topic_ids': TopicModel,
                'subtopic_ids': SubtopicModel,
                'concept_ids': ConceptModel,
            }
            related_items = db.query(model_map[key]).filter(model_map[key].id.in_(value)).all()
            setattr(db_question, key.replace('_ids', 's'), related_items)
        
        else:
            setattr(db_question, key, value)


def create_question_in_db(db: Session, question_data: Dict) -> QuestionModel:
    """Creates a new question in the database."""
    db_question = QuestionModel(
        text=question_data['text'],
        difficulty=DifficultyLevel(question_data['difficulty'])
        if isinstance(question_data['difficulty'], str)
        else question_data['difficulty']
    )
    db.add(db_question)
    db.flush()

    # Associate related models
    associate_related_models(db, db_question, question_data)

    db.commit()
    db.refresh(db_question)
    return db_question

def read_question_from_db(db: Session, question_id: int) -> Optional[QuestionModel]:
    return db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

def read_questions_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    return db.query(QuestionModel).offset(skip).limit(limit).all()

def update_question_in_db(db: Session, question_id: int, update_data: Dict) -> Optional[QuestionModel]:
    """Updates an existing question in the database."""
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

    if db_question is None:
        return None

    # Update simple fields
    for key, value in update_data.items():
        if key not in ['answer_choices', 'question_tag_ids', 'question_set_ids', 'subject_ids', 'topic_ids', 'subtopic_ids', 'concept_ids']:
            setattr(db_question, key, value)

    # Update associations
    associate_related_models(db, db_question, update_data)

    db.commit()
    db.refresh(db_question)
    return db_question

def delete_question_from_db(db: Session, question_id: int) -> bool:
    db_question = read_question_from_db(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False
