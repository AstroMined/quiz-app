# filename: app/crud/crud_questions.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.questions import QuestionModel, DifficultyLevel
from app.models.answer_choices import AnswerChoiceModel
from app.models.question_tags import QuestionTagModel
from app.models.question_sets import QuestionSetModel

def create_question(db: Session, question_data: dict) -> QuestionModel:
    db_question = QuestionModel(
        text=question_data['text'],
        difficulty=DifficultyLevel(question_data['difficulty'])
    )
    db.add(db_question)
    db.flush()

    if 'answer_choices' in question_data:
        for answer_choice_data in question_data['answer_choices']:
            db_answer_choice = AnswerChoiceModel(**answer_choice_data)
            db.add(db_answer_choice)
            db_question.answer_choices.append(db_answer_choice)

    if 'question_tag_ids' in question_data:
        tags = db.query(QuestionTagModel).filter(QuestionTagModel.id.in_(question_data['question_tag_ids'])).all()
        db_question.question_tags = tags

    if 'question_set_ids' in question_data:
        question_sets = db.query(QuestionSetModel).filter(QuestionSetModel.id.in_(question_data['question_set_ids'])).all()
        db_question.question_sets = question_sets

    db.commit()
    db.refresh(db_question)
    return db_question

def get_question(db: Session, question_id: int) -> Optional[QuestionModel]:
    return db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

def get_questions(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    return db.query(QuestionModel).offset(skip).limit(limit).all()

def update_question(db: Session, question_id: int, question_data: dict) -> Optional[QuestionModel]:
    db_question = get_question(db, question_id)
    if db_question:
        for key, value in question_data.items():
            if key == 'difficulty':
                setattr(db_question, key, DifficultyLevel(value))
            elif key == 'answer_choices':
                db_question.answer_choices = []
                for answer_choice_data in value:
                    db_answer_choice = AnswerChoiceModel(**answer_choice_data)
                    db.add(db_answer_choice)
                    db_question.answer_choices.append(db_answer_choice)
            elif key == 'question_tag_ids':
                tags = db.query(QuestionTagModel).filter(QuestionTagModel.id.in_(value)).all()
                db_question.question_tags = tags
            elif key == 'question_set_ids':
                question_sets = db.query(QuestionSetModel).filter(QuestionSetModel.id.in_(value)).all()
                db_question.question_sets = question_sets
            else:
                setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int) -> bool:
    db_question = get_question(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False
