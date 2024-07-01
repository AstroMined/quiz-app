# filename: app/crud/crud_answer_choices.py

from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.answer_choices import AnswerChoiceModel
from app.schemas.answer_choices import AnswerChoiceCreateSchema

def create_answer_choice_crud(db: Session, answer_choice: AnswerChoiceCreateSchema) -> AnswerChoiceModel:
    db_answer_choice = AnswerChoiceModel(**answer_choice.model_dump())
    db.add(db_answer_choice)
    db.commit()
    db.refresh(db_answer_choice)
    return db_answer_choice

def create_answer_choices_bulk(db: Session, answer_choices: List[AnswerChoiceCreateSchema], question_id: int) -> List[AnswerChoiceModel]:
    db_answer_choices = [
        AnswerChoiceModel(
            text=choice.text,
            is_correct=choice.is_correct,
            explanation=choice.explanation,
            question_id=question_id
        )
        for choice in answer_choices
    ]
    db.add_all(db_answer_choices)
    db.commit()
    for db_choice in db_answer_choices:
        db.refresh(db_choice)
    return db_answer_choices

def read_answer_choice_crud(db: Session, answer_choice_id: int) -> AnswerChoiceModel:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == answer_choice_id).first()

def update_answer_choice_crud(db: Session, answer_choice_id: int, answer_choice: AnswerChoiceCreateSchema) -> AnswerChoiceModel:
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id)
    if db_answer_choice:
        update_data = answer_choice.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_answer_choice, key, value)
        db.commit()
        db.refresh(db_answer_choice)
    return db_answer_choice

def update_answer_choices_bulk(db: Session, question_id: int, new_answer_choices: List[Dict]) -> List[AnswerChoiceModel]:
    # Get existing answer choices
    existing_choices = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.question_id == question_id).all()
    existing_choices_dict = {choice.id: choice for choice in existing_choices}

    updated_choices = []
    for choice_data in new_answer_choices:
        if 'id' in choice_data and choice_data['id'] in existing_choices_dict:
            # Update existing choice
            choice = existing_choices_dict[choice_data['id']]
            for key, value in choice_data.items():
                setattr(choice, key, value)
            updated_choices.append(choice)
        else:
            # Create new choice
            new_choice = AnswerChoiceModel(question_id=question_id, **choice_data)
            db.add(new_choice)
            updated_choices.append(new_choice)

    # Remove choices that are not in the new data
    for choice in existing_choices:
        if choice not in updated_choices:
            db.delete(choice)

    db.flush()
    return updated_choices

def delete_answer_choice_crud(db: Session, answer_choice_id: int) -> None:
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id)
    if db_answer_choice:
        db.delete(db_answer_choice)
        db.commit()
