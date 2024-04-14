# filename: app/crud/crud_questions.py

from typing import List
from sqlalchemy.orm import Session, joinedload
from app.models import QuestionModel, AnswerChoiceModel
from app.schemas import QuestionCreateSchema, QuestionUpdateSchema
from app.services import randomize_questions, randomize_answer_choices

def create_question_crud(db: Session, question: QuestionCreateSchema) -> QuestionModel:
    db_question = QuestionModel(
        text=question.text,
        subject_id=question.subject_id,
        topic_id=question.topic_id,
        subtopic_id=question.subtopic_id,
        difficulty=question.difficulty
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.answer_choices:
        db_choice = AnswerChoiceModel(
            text=choice.text,
            is_correct=choice.is_correct,
            explanation=choice.explanation,
            question_id=db_question.id
        )
        db.add(db_choice)

    db_question.question_set_ids = question.question_set_ids

    db.commit()
    return db_question

def get_questions_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    questions = db.query(QuestionModel).offset(skip).limit(limit).all()
    questions = randomize_questions(questions)  # Randomize the order of questions
    for question in questions:
        question.answer_choices = randomize_answer_choices(question.answer_choices)  # Randomize the order of answer choices
    return questions

def get_question_crud(db: Session, question_id: int) -> QuestionModel:
    return db.query(QuestionModel).options(
        joinedload(QuestionModel.subject),
        joinedload(QuestionModel.topic),
        joinedload(QuestionModel.subtopic),
        joinedload(QuestionModel.tags),
        joinedload(QuestionModel.answer_choices)
    ).filter(QuestionModel.id == question_id).first()

def update_question_crud(db: Session, question_id: int, question: QuestionUpdateSchema) -> QuestionModel:
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not db_question:
        return None

    update_data = question.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "answer_choices":
            # Remove existing answer choices
            db_question.answer_choices = []
            db.commit()

            for choice_data in value:
                db_choice = AnswerChoiceModel(
                    text=choice_data["text"],
                    is_correct=choice_data["is_correct"],
                    explanation=choice_data["explanation"],
                    question_id=db_question.id
                )
                db.add(db_choice)
        else:
            setattr(db_question, field, value)

    if question.question_set_ids is not None:
        db_question.question_set_ids = question.question_set_ids

    db.commit()
    db.refresh(db_question)
    return db_question

def delete_question_crud(db: Session, question_id: int) -> bool:
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False
