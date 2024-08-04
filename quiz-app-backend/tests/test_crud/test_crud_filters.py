# filename: tests/test_crud_filters.py

import pytest
from pydantic import ValidationError
from app.crud.crud_filters import filter_questions_crud


def test_filter_questions_extra_invalid_parameter(db_session):
    # Test case: Extra invalid parameter
    filters = {
        "subject": "Math",
        "invalid_param": "InvalidValue"
    }
    with pytest.raises(ValidationError) as exc_info:
        filter_questions_crud(db=db_session, filters=filters)
    assert "Extra inputs are not permitted" in str(exc_info.value)

def test_filter_questions_invalid_parameter_type(db_session):
    # Test case: Invalid parameter type
    filters = {
        "subject": 123,  # Invalid type, should be a string
        "topic": "Geometry"
    }
    with pytest.raises(ValidationError) as exc_info:
        filter_questions_crud(db=db_session, filters=filters)
    assert "Input should be a valid string" in str(exc_info.value)

def test_filter_questions_invalid_tag_type(db_session):
    # Test case: Invalid tag type
    filters = {
        "question_tags": "InvalidTag"  # Invalid type, should be a list of strings
    }
    with pytest.raises(ValidationError) as exc_info:
        filter_questions_crud(db=db_session, filters=filters)
    assert "Input should be a valid list" in str(exc_info.value)

def test_filter_questions_no_filters(db_session):
    # Test case: No filters provided
    filters = {}
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result is None

def test_filter_questions_invalid_subject(db_session):
    # Test case: Invalid subject filter
    filters = {
        "subject": "InvalidSubject"
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_topic(db_session):
    # Test case: Invalid topic filter
    filters = {
        "topic": "InvalidTopic"
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_subtopic(db_session):
    # Test case: Invalid subtopic filter
    filters = {
        "subtopic": "InvalidSubtopic"
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_difficulty(db_session):
    # Test case: Invalid difficulty filter
    filters = {
        "difficulty": "InvalidDifficulty"
    }
    with pytest.raises(ValidationError) as excinfo:
        result = filter_questions_crud(db=db_session, filters=filters)
    assert "Invalid difficulty. Must be one of: Beginner, Easy, Medium, Hard, Expert" in str(excinfo.value)

def test_filter_questions_invalid_tags(db_session):
    # Test case: Invalid tags filter
    filters = {
        "question_tags": ["InvalidTag"]
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_valid_filters(db_session, test_questions):
    # Test case: Valid filters
    subject = test_questions[0].subject
    topic = test_questions[0].topic
    subtopic = test_questions[0].subtopic
    difficulty = test_questions[0].difficulty
    question_tags = [tag.tag for tag in test_questions[0].question_tags]

    filters = {
        "subject": subject.name,
        "topic": topic.name,
        "subtopic": subtopic.name,
        "difficulty": difficulty,
        "question_tags": question_tags
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert len(result) == 1
    assert result[0].id == test_questions[0].id
