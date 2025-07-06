# filename: backend/tests/test_crud/test_crud_filters.py

import pytest

from backend.app.crud.crud_filters import read_filtered_questions_from_db
from backend.app.crud.crud_question_tags import (
    create_question_tag_in_db,
    create_question_to_tag_association_in_db,
)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subjects import create_question_to_subject_association_in_db
from backend.app.models.questions import DifficultyLevel
from backend.app.services.logging_service import logger


def test_read_filtered_questions_no_filter(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {})
    # Verify that our test question is present in the results
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_by_subject(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session, {"subject": filter_test_data["subject"].name}
    )
    # Verify that our test question is present in the results when filtering by subject
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_by_topic(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session, {"topic": filter_test_data["topic"].name}
    )
    # Verify that our test question is present in the results when filtering by topic
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_by_subtopic(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session, {"subtopic": filter_test_data["subtopic"].name}
    )
    # Verify that our test question is present in the results when filtering by subtopic
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_by_difficulty(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session, {"difficulty": DifficultyLevel.MEDIUM.value}
    )
    # Verify that our test question is present in the results when filtering by difficulty
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_by_tag(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session, {"question_tags": [filter_test_data["tag"].tag]}
    )
    # Verify that our test question is present in the results when filtering by tag
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_multiple_filters(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session,
        {
            "subject": filter_test_data["subject"].name,
            "topic": filter_test_data["topic"].name,
            "subtopic": filter_test_data["subtopic"].name,
            "difficulty": DifficultyLevel.MEDIUM.value,
            "question_tags": [filter_test_data["tag"].tag],
        },
    )
    # Verify that our test question is present when using multiple filters
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_non_matching_filter(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session, {"subject": "Non-existent Subject"}
    )
    assert len(results) == 0


def test_read_filtered_questions_case_insensitive(db_session, filter_test_data):
    results = read_filtered_questions_from_db(
        db_session, {"subject": filter_test_data["subject"].name.upper()}
    )
    # Verify that our test question is present when using case-insensitive filtering
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_partial_tag_match(db_session, filter_test_data):
    partial_tag = filter_test_data["tag"].tag[:3]  # Take first 3 characters of the tag
    results = read_filtered_questions_from_db(
        db_session, {"question_tags": [partial_tag]}
    )
    assert len(results) == 0


def test_read_filtered_questions_multiple_tags(
    db_session, filter_test_data, test_schema_question_tag
):
    # Create a new tag and associate it with the existing question
    new_tag_data = {"tag": "New Tag"}
    new_tag = create_question_tag_in_db(db_session, new_tag_data)
    logger.debug("New tag: %s", new_tag)
    assert new_tag.id is not None
    assert new_tag.tag == new_tag_data["tag"]
    create_question_to_tag_association_in_db(
        db_session, filter_test_data["question"].id, new_tag.id
    )

    results = read_filtered_questions_from_db(
        db_session, {"question_tags": [filter_test_data["tag"].tag, new_tag.tag]}
    )
    logger.debug("Results: %s", results)
    # Verify that our test question is present when filtering by multiple tags
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
    # Verify we have at least our test question
    assert len(results) >= 1


def test_read_filtered_questions_pagination(
    db_session, filter_test_data, test_schema_question
):
    # Create additional questions
    for i in range(5):
        new_question_data = test_schema_question.model_dump()
        new_question_data["text"] = f"Additional Question {i}"
        new_question = create_question_in_db(db_session, new_question_data)
        create_question_to_subject_association_in_db(
            db_session, new_question.id, filter_test_data["subject"].id
        )

    # Test pagination
    results_page1 = read_filtered_questions_from_db(
        db_session, {"subject": filter_test_data["subject"].name}, skip=0, limit=3
    )
    results_page2 = read_filtered_questions_from_db(
        db_session, {"subject": filter_test_data["subject"].name}, skip=3, limit=3
    )

    assert len(results_page1) == 3
    assert len(results_page2) == 3
    assert set(q.id for q in results_page1).isdisjoint(set(q.id for q in results_page2))


def test_read_filtered_questions_no_results(db_session):
    results = read_filtered_questions_from_db(
        db_session,
        {
            "subject": "Non-existent Subject",
            "topic": "Non-existent Topic",
            "subtopic": "Non-existent Subtopic",
            "difficulty": DifficultyLevel.EXPERT.value,
            "question_tags": ["non-existent-tag"],
        },
    )
    assert len(results) == 0


def test_read_filtered_questions_empty_tag_list(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"question_tags": []})
    # Should return all questions when tag filter is empty
    assert len(results) >= 1
    # Should include our test question
    question_ids = [q.id for q in results]
    assert filter_test_data["question"].id in question_ids
