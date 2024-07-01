# filename: app/crud/crud_questions.py

from typing import List
from sqlalchemy.orm import Session, joinedload
from app.crud.crud_answer_choices import create_answer_choices_bulk, update_answer_choices_bulk
from app.crud.crud_question_tag_associations import add_tag_to_question
from app.models.questions import QuestionModel
from app.models.associations import QuestionToTagAssociation
from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema
from app.services.randomization_service import randomize_questions, randomize_answer_choices
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

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
    logger.debug("Question created: %s", sqlalchemy_obj_to_dict(db_question))

    if question.answer_choices:
        answer_choices = create_answer_choices_bulk(db, question.answer_choices, db_question.id)
        for choice in answer_choices:
            db_question.answer_choices.append(choice)
            logger.debug("Answer choices created: %s", sqlalchemy_obj_to_dict(choice))
        db.commit()

    if question.question_set_ids:
        db_question.question_set_ids = question.question_set_ids
        db.commit()

    logger.debug("Question before the return: %s", sqlalchemy_obj_to_dict(db_question))

    return db_question

def read_questions_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    questions = db.query(QuestionModel).offset(skip).limit(limit).all()
    questions = randomize_questions(questions)  # Randomize the order of questions
    for question in questions:
        question.answer_choices = randomize_answer_choices(question.answer_choices)  # Randomize the order of answer choices
    return questions

def read_question_crud(db: Session, question_id: int) -> QuestionModel:
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
    
    if "answer_choices" in update_data:
        answer_choices = update_data.pop("answer_choices")
        update_answer_choices_bulk(db, question_id, answer_choices)

    if "tags" in update_data:
        # Remove existing tags
        db.query(QuestionToTagAssociation).filter_by(question_id=question_id).delete()
        # Add new tags
        for tag_id in update_data["tags"]:
            add_tag_to_question(db, question_id, tag_id)

    for field, value in update_data.items():
        setattr(db_question, field, value)

    if question.question_set_ids is not None:
        db_question.question_set_ids = question.question_set_ids

    db.flush()
    db.refresh(db_question)
    return db_question

def delete_question_crud(db: Session, question_id: int) -> bool:
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False
