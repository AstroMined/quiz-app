import pytest
from pydantic import ValidationError
from app.crud.crud_filters import filter_questions_crud
from app.schemas.filters import FilterParamsSchema

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
        "tags": "InvalidTag"  # Invalid type, should be a list of strings
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
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_tags(db_session):
    # Test case: Invalid tags filter
    filters = {
        "tags": ["InvalidTag"]
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_valid_filters(db_session, test_question):
    # Test case: Valid filters
    subject = test_question.subject
    topic = test_question.topic
    subtopic = test_question.subtopic
    difficulty = test_question.difficulty
    tags = [tag.tag for tag in test_question.tags]

    filters = {
        "subject": subject.name,
        "topic": topic.name,
        "subtopic": subtopic.name,
        "difficulty": difficulty,
        "tags": tags
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert len(result) == 1
    assert result[0].id == test_question.id
