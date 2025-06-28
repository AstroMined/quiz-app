# filename: backend/tests/crud/test_crud_answer_choices.py

from backend.app.crud.crud_answer_choices import (
    create_answer_choice_in_db,
    create_question_to_answer_association_in_db,
    delete_answer_choice_from_db,
    delete_question_to_answer_association_from_db,
    read_answer_choice_from_db,
    read_answer_choices_for_question_from_db,
    read_answer_choices_from_db,
    read_questions_for_answer_choice_from_db,
    update_answer_choice_in_db,
)
from backend.app.crud.crud_questions import create_question_in_db


def test_create_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    assert answer_choice.text == test_schema_answer_choice.text
    assert answer_choice.is_correct == test_schema_answer_choice.is_correct
    assert answer_choice.explanation == test_schema_answer_choice.explanation


def test_read_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    read_choice = read_answer_choice_from_db(db_session, answer_choice.id)
    assert read_choice.id == answer_choice.id
    assert read_choice.text == answer_choice.text


def test_read_answer_choices(db_session, test_schema_answer_choice):
    create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    choices = read_answer_choices_from_db(db_session)
    assert len(choices) > 0


def test_update_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    updated_data = {"text": "Updated text"}
    updated_choice = update_answer_choice_in_db(
        db_session, answer_choice.id, updated_data
    )
    assert updated_choice.text == "Updated text"


def test_delete_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    assert delete_answer_choice_from_db(db_session, answer_choice.id) is True
    assert read_answer_choice_from_db(db_session, answer_choice.id) is None


def test_create_question_to_answer_association(
    db_session, test_schema_question, test_schema_answer_choice
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    assert (
        create_question_to_answer_association_in_db(
            db_session, question.id, answer_choice.id
        )
        is True
    )


def test_delete_question_to_answer_association(
    db_session, test_schema_question, test_schema_answer_choice
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    create_question_to_answer_association_in_db(
        db_session, question.id, answer_choice.id
    )
    assert (
        delete_question_to_answer_association_from_db(
            db_session, question.id, answer_choice.id
        )
        is True
    )


def test_read_answer_choices_for_question(
    db_session, test_schema_question, test_schema_answer_choice
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    create_question_to_answer_association_in_db(
        db_session, question.id, answer_choice.id
    )
    choices = read_answer_choices_for_question_from_db(db_session, question.id)
    assert len(choices) == 1
    assert choices[0].id == answer_choice.id


def test_read_questions_for_answer_choice(
    db_session, test_schema_question, test_schema_answer_choice
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    create_question_to_answer_association_in_db(
        db_session, question.id, answer_choice.id
    )
    questions = read_questions_for_answer_choice_from_db(db_session, answer_choice.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
