# filename: backend/tests/crud/test_crud_filters.py

from backend.app.crud.crud_filters import read_filtered_questions_from_db
from backend.app.models.questions import DifficultyLevel


def test_read_filtered_questions_no_filter(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_subject(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"subject": filter_test_data["subject"].name})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_topic(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"topic": filter_test_data["topic"].name})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_subtopic(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"subtopic": filter_test_data["subtopic"].name})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_difficulty(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"difficulty": DifficultyLevel.MEDIUM.value})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_tag(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"question_tags": [filter_test_data["tag"].tag]})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_multiple_filters(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {
        "subject": filter_test_data["subject"].name,
        "topic": filter_test_data["topic"].name,
        "subtopic": filter_test_data["subtopic"].name,
        "difficulty": DifficultyLevel.MEDIUM.value,
        "question_tags": [filter_test_data["tag"].tag]
    })
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_non_matching_filter(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"subject": "Non-existent Subject"})
    assert len(results) == 0
