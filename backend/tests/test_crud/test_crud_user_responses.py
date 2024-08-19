# filename: backend/tests/crud/test_crud_user_responses.py

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.crud.crud_answer_choices import create_answer_choice_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_user import create_user_in_db
from backend.app.crud.crud_user_responses import (
    create_user_response_in_db, delete_user_response_from_db,
    read_user_response_from_db, read_user_responses_for_question_from_db,
    read_user_responses_for_user_from_db, read_user_responses_from_db,
    update_user_response_in_db)


def test_create_user_response(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    assert user_response.user_id == user.id
    assert user_response.question_id == question.id
    assert user_response.answer_choice_id == answer_choice.id
    assert user_response.is_correct == user_response_data["is_correct"]

def test_read_user_response(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    read_response = read_user_response_from_db(db_session, user_response.id)
    assert read_response.id == user_response.id
    assert read_response.user_id == user_response.user_id
    assert read_response.question_id == user_response.question_id

def test_read_user_responses(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    responses = read_user_responses_from_db(db_session)
    assert len(responses) > 0

def test_update_user_response(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    
    # Store the original is_correct value
    original_is_correct = user_response.is_correct
    
    updated_data = {"is_correct": not original_is_correct}
    
    updated_response = update_user_response_in_db(db_session, user_response.id, updated_data)
    
    # Fetch the response from the database again to ensure it's updated
    fetched_response = read_user_response_from_db(db_session, user_response.id)
    
    assert updated_response.is_correct != original_is_correct, f"Updated response is_correct ({updated_response.is_correct}) should not equal original is_correct ({original_is_correct})"
    assert fetched_response.is_correct != original_is_correct, f"Fetched response is_correct ({fetched_response.is_correct}) should not equal original is_correct ({original_is_correct})"

def test_delete_user_response(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    assert delete_user_response_from_db(db_session, user_response.id) is True
    assert read_user_response_from_db(db_session, user_response.id) is None

def test_read_user_responses_for_user(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    user_responses = read_user_responses_for_user_from_db(db_session, user.id)
    assert len(user_responses) == 1
    assert user_responses[0].user_id == user.id

def test_read_user_responses_for_question(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    question_responses = read_user_responses_for_question_from_db(db_session, question.id)
    assert len(question_responses) == 1
    assert question_responses[0].question_id == question.id

def test_read_user_responses_with_time_range(db_session, test_schema_user_response, test_schema_user, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    
    start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    end_time = datetime.now(timezone.utc) + timedelta(hours=1)
    
    responses = read_user_responses_from_db(db_session, start_time=start_time, end_time=end_time)
    assert len(responses) == 1
    
    past_start_time = datetime.now(timezone.utc) - timedelta(days=2)
    past_end_time = datetime.now(timezone.utc) - timedelta(days=1)
    
    past_responses = read_user_responses_from_db(db_session, start_time=past_start_time, end_time=past_end_time)
    assert len(past_responses) == 0
