# filename: backend/tests/test_crud/test_crud_questions.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_answer_choices import (
    create_answer_choice_in_db,
    read_answer_choices_for_question_from_db,
    read_answer_choices_from_db,
)
from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.crud.crud_questions import (
    create_question_in_db,
    delete_question_from_db,
    read_full_question_from_db,
    read_question_from_db,
    read_questions_from_db,
    replace_question_in_db,
    update_question_in_db,
)
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.models.associations import QuestionToAnswerAssociation
from backend.app.models.questions import DifficultyLevel
from backend.app.services.logging_service import logger, sqlalchemy_obj_to_dict


def test_create_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert question.text == test_schema_question.text
    assert question.difficulty == test_schema_question.difficulty


def test_create_question_with_answers(db_session, test_schema_question_with_answers):
    # Ensure no questions exist before creating a new one
    existing_questions = read_questions_from_db(db_session)
    assert len(existing_questions) == 0

    # Ensure no answer choices exist before creating a new question
    existing_answer_choices = read_answer_choices_from_db(db_session)
    assert len(existing_answer_choices) == 0

    question_data = test_schema_question_with_answers.model_dump()
    created_question = create_question_in_db(db_session, question_data)
    stored_question = read_full_question_from_db(db_session, created_question.id)
    assert stored_question.text == test_schema_question_with_answers.text
    assert stored_question.difficulty == test_schema_question_with_answers.difficulty
    assert len(stored_question.answer_choices) == len(
        test_schema_question_with_answers.answer_choices
    )
    assert (
        stored_question.answer_choices[0].text
        == test_schema_question_with_answers.answer_choices[0].text
    )
    assert (
        stored_question.concepts[0].id in test_schema_question_with_answers.concept_ids
    )
    assert (
        stored_question.subjects[0].id in test_schema_question_with_answers.subject_ids
    )
    assert stored_question.topics[0].id in test_schema_question_with_answers.topic_ids
    assert (
        stored_question.subtopics[0].id
        in test_schema_question_with_answers.subtopic_ids
    )

    new_answer_choices = read_answer_choices_from_db(db_session)
    assert len(new_answer_choices) == len(
        test_schema_question_with_answers.answer_choices
    )
    question_answer_choices = read_answer_choices_for_question_from_db(
        db_session, created_question.id
    )
    for ac in question_answer_choices:
        assert created_question.id in [q.id for q in ac.questions]

    # Read all associations in QuestionToAnswerAssociation table
    question_to_answer_associations = db_session.query(
        QuestionToAnswerAssociation
    ).all()
    for qta in question_to_answer_associations:
        assert qta.question_id == created_question.id
    assert created_question.text == test_schema_question_with_answers.text
    assert created_question.difficulty == test_schema_question_with_answers.difficulty
    assert len(created_question.answer_choices) == len(
        test_schema_question_with_answers.answer_choices
    )


def test_read_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    read_question = read_question_from_db(db_session, question.id)
    assert read_question.id == question.id
    assert read_question.text == question.text


def test_read_questions(db_session, test_schema_question):
    create_question_in_db(db_session, test_schema_question.model_dump())
    questions = read_questions_from_db(db_session)
    assert len(questions) > 0


def test_update_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {"text": "Updated question text", "difficulty": DifficultyLevel.HARD}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert updated_question.text == "Updated question text"
    assert updated_question.difficulty == DifficultyLevel.HARD


def test_delete_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert delete_question_from_db(db_session, question.id) is True
    assert read_question_from_db(db_session, question.id) is None


def test_create_question_with_associations(
    db_session,
    test_schema_question,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    question_data = test_schema_question.model_dump()
    question_data.update(
        {
            "subject_ids": [test_model_subject.id],
            "topic_ids": [test_model_topic.id],
            "subtopic_ids": [test_model_subtopic.id],
            "concept_ids": [test_model_concept.id],
        }
    )
    question = create_question_in_db(db_session, question_data)
    assert len(question.subjects) == 1
    assert len(question.topics) == 1
    assert len(question.subtopics) == 1
    assert len(question.concepts) == 1


def test_update_question_associations(
    db_session,
    test_schema_question,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
    }
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.subjects) == 1
    assert len(updated_question.topics) == 1
    assert len(updated_question.subtopics) == 1
    assert len(updated_question.concepts) == 1


def test_create_question_with_invalid_difficulty(db_session, test_schema_question):
    invalid_question_data = test_schema_question.model_dump()
    invalid_question_data["difficulty"] = "INVALID_DIFFICULTY"
    with pytest.raises(ValueError):
        create_question_in_db(db_session, invalid_question_data)


def test_create_question_with_empty_text(db_session, test_schema_question):
    invalid_question_data = test_schema_question.model_dump()
    invalid_question_data["text"] = ""
    with pytest.raises(ValueError):
        create_question_in_db(db_session, invalid_question_data)


def test_read_nonexistent_question(db_session):
    nonexistent_id = 9999
    assert read_question_from_db(db_session, nonexistent_id) is None


def test_update_nonexistent_question(db_session):
    nonexistent_id = 9999
    updated_data = {"text": "Updated question text"}
    assert update_question_in_db(db_session, nonexistent_id, updated_data) is None


def test_delete_nonexistent_question(db_session):
    nonexistent_id = 9999
    assert delete_question_from_db(db_session, nonexistent_id) is False


def test_create_question_with_multiple_subjects(
    db_session, test_schema_question, test_model_subject
):
    new_subject = create_subject_in_db(db_session, {"name": "New Subject"})
    question_data = test_schema_question.model_dump()
    question_data["subject_ids"] = [test_model_subject.id, new_subject.id]
    question = create_question_in_db(db_session, question_data)
    assert len(question.subjects) == 2
    assert test_model_subject.id in [subject.id for subject in question.subjects]
    assert new_subject.id in [subject.id for subject in question.subjects]


def test_update_question_remove_associations(
    db_session, test_schema_question, test_model_subject, test_model_topic
):
    question_data = test_schema_question.model_dump()
    question_data.update(
        {"subject_ids": [test_model_subject.id], "topic_ids": [test_model_topic.id]}
    )
    question = create_question_in_db(db_session, question_data)

    updated_data = {"subject_ids": [], "topic_ids": []}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.subjects) == 0
    assert len(updated_question.topics) == 0


def test_create_question_with_tags(
    db_session, test_schema_question, test_schema_question_tag
):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question_data = test_schema_question.model_dump()
    question_data["question_tag_ids"] = [tag.id]
    question = create_question_in_db(db_session, question_data)
    assert len(question.question_tags) == 1
    assert question.question_tags[0].id == tag.id


def test_update_question_tags(
    db_session, test_schema_question, test_schema_question_tag
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())

    updated_data = {"question_tag_ids": [tag.id]}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.question_tags) == 1
    assert updated_question.question_tags[0].id == tag.id


def test_create_question_with_answer_choices(
    db_session, test_schema_question, test_schema_answer_choice
):
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )
    question_data = test_schema_question.model_dump()
    question_data["answer_choice_ids"] = [answer_choice.id]
    question = create_question_in_db(db_session, question_data)
    assert len(question.answer_choices) == 1
    assert question.answer_choices[0].id == answer_choice.id


def test_update_question_answer_choices(
    db_session, test_schema_question, test_schema_answer_choice
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )

    updated_data = {"answer_choice_ids": [answer_choice.id]}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.answer_choices) == 1
    assert updated_question.answer_choices[0].id == answer_choice.id


def test_read_questions_pagination(db_session, test_schema_question):
    for i in range(5):
        create_question_in_db(
            db_session, {**test_schema_question.model_dump(), "text": f"Question {i}"}
        )

    page1 = read_questions_from_db(db_session, skip=0, limit=2)
    page2 = read_questions_from_db(db_session, skip=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


def test_create_question_with_creator(
    db_session, test_schema_question, test_model_user
):
    question_data = test_schema_question.model_dump()
    question_data["creator_id"] = test_model_user.id
    question = create_question_in_db(db_session, question_data)
    assert question.creator_id == test_model_user.id


def test_update_question_creator(db_session, test_schema_question, test_model_user):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {"creator_id": test_model_user.id}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert updated_question.creator_id == test_model_user.id


def test_replace_question(
    db_session, test_schema_question, test_model_subject, test_model_topic
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    replace_data = {
        "text": "Replaced question text",
        "difficulty": DifficultyLevel.EXPERT,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [],
        "concept_ids": [],
        "answer_choice_ids": [],
        "question_tag_ids": [],
        "question_set_ids": [],
    }
    replaced_question = replace_question_in_db(db_session, question.id, replace_data)
    assert replaced_question.text == "Replaced question text"
    assert replaced_question.difficulty == DifficultyLevel.EXPERT
    assert len(replaced_question.subjects) == 1
    assert len(replaced_question.topics) == 1
    assert len(replaced_question.subtopics) == 0
    assert len(replaced_question.concepts) == 0
    assert len(replaced_question.answer_choices) == 0
    assert len(replaced_question.question_tags) == 0
    assert len(replaced_question.question_sets) == 0


def test_replace_question_with_new_answer_choices(
    db_session, test_schema_question, test_schema_answer_choice
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    new_answer_choice_data = test_schema_answer_choice.model_dump()
    replace_data = {
        "text": "Replaced question with new answers",
        "difficulty": DifficultyLevel.MEDIUM,
        "subject_ids": [],
        "topic_ids": [],
        "subtopic_ids": [],
        "concept_ids": [],
        "new_answer_choices": [new_answer_choice_data],
        "question_tag_ids": [],
        "question_set_ids": [],
    }
    replaced_question = replace_question_in_db(db_session, question.id, replace_data)
    assert replaced_question.text == "Replaced question with new answers"
    assert len(replaced_question.answer_choices) == 1
    assert replaced_question.answer_choices[0].text == new_answer_choice_data["text"]


def test_replace_nonexistent_question(db_session):
    nonexistent_id = 9999
    replace_data = {
        "text": "Replaced question text",
        "difficulty": DifficultyLevel.EASY,
    }
    assert replace_question_in_db(db_session, nonexistent_id, replace_data) is None


# Update existing test to cover more partial update scenarios
def test_update_question_partial(
    db_session, test_schema_question, test_model_subject, test_model_topic
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    initial_difficulty = question.difficulty
    initial_subject_count = len(question.subjects)
    new_subject = create_subject_in_db(db_session, {"name": "New Subject"})

    # Partial update: only change text and add a subject
    partial_update_data = {
        "text": "Partially updated question text",
        "subject_ids": [new_subject.id],
    }
    updated_question = update_question_in_db(
        db_session, question.id, partial_update_data
    )

    assert updated_question.text == "Partially updated question text"
    assert updated_question.difficulty == initial_difficulty  # Should remain unchanged
    assert len(updated_question.subjects) == initial_subject_count + 1
    assert new_subject.id in [subject.id for subject in updated_question.subjects]
    assert test_model_subject.id in [
        subject.id for subject in updated_question.subjects
    ]

    # Another partial update: change difficulty and add a topic
    another_partial_update = {
        "difficulty": DifficultyLevel.HARD,
        "topic_ids": [test_model_topic.id],
    }
    updated_question = update_question_in_db(
        db_session, question.id, another_partial_update
    )

    assert (
        updated_question.text == "Partially updated question text"
    )  # Should remain from previous update
    assert updated_question.difficulty == DifficultyLevel.HARD
    assert len(updated_question.topics) == 1


def test_update_question_mixed_answer_choices(
    db_session, test_schema_question, test_schema_answer_choice
):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    existing_answer = create_answer_choice_in_db(
        db_session, test_schema_answer_choice.model_dump()
    )

    update_data = {
        "answer_choice_ids": [existing_answer.id],
        "new_answer_choices": [{"text": "New answer", "is_correct": False}],
    }

    updated_question = update_question_in_db(db_session, question.id, update_data)
    assert len(updated_question.answer_choices) == 2
    assert any(ac.id == existing_answer.id for ac in updated_question.answer_choices)
    assert any(ac.text == "New answer" for ac in updated_question.answer_choices)


def test_create_question_with_none_text(db_session, test_schema_question):
    invalid_question_data = test_schema_question.model_dump()
    invalid_question_data["text"] = None
    with pytest.raises(ValueError, match="Question text cannot be None or empty"):
        create_question_in_db(db_session, invalid_question_data)


def test_create_question_with_answer_choice_without_question_ids(
    db_session, test_schema_question
):
    question_data = test_schema_question.model_dump()
    question_data["new_answer_choices"] = [
        {"text": "Answer without question_ids", "is_correct": True}
    ]
    question = create_question_in_db(db_session, question_data)
    assert len(question.answer_choices) == 1
    assert question.answer_choices[0].text == "Answer without question_ids"
    assert question.id in [q.id for q in question.answer_choices[0].questions]


def test_replace_question_with_invalid_data(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    question_data = sqlalchemy_obj_to_dict(question)
    question_data["difficulty"] = "INVALID_DIFFICULTY"
    question_data["text"] = "Replaced question text"

    with pytest.raises(LookupError):  # We expect a LookupError to be raised
        replace_question_in_db(db_session, question_data["id"], question_data)

    # Verify that the original question remains unchanged
    unchanged_question = read_question_from_db(db_session, question_data["id"])
    assert unchanged_question.text == test_schema_question.text
    assert unchanged_question.difficulty == test_schema_question.difficulty


def test_update_question_with_invalid_data(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    logger.debug("Question: %s", sqlalchemy_obj_to_dict(question))
    assert question.difficulty == test_schema_question.difficulty

    # Attempt to update the question with invalid data
    invalid_update_data = {
        "difficulty": "INVALID_DIFFICULTY",  # This should cause an exception
    }

    with pytest.raises(LookupError):  # We expect a LookupError to be raised
        logger.debug("Attempting to update question with invalid data")
        updated_question = update_question_in_db(
            db_session, question.id, invalid_update_data
        )
        logger.debug("Updated Question: %s", sqlalchemy_obj_to_dict(updated_question))

    # Verify that the original question remains unchanged
    unchanged_question = read_question_from_db(db_session, question.id)
    assert unchanged_question.difficulty == test_schema_question.difficulty
