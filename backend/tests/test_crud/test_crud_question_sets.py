# filename: backend/tests/test_crud/test_crud_question_sets.py

import pytest

from backend.app.crud.crud_groups import create_group_in_db
from backend.app.crud.crud_question_sets import (
    create_question_set_in_db,
    create_question_set_to_group_association_in_db,
    create_question_set_to_question_association_in_db,
    delete_question_set_from_db,
    delete_question_set_to_group_association_from_db,
    delete_question_set_to_question_association_from_db,
    read_groups_for_question_set_from_db,
    read_question_set_from_db,
    read_question_sets_from_db,
    read_questions_for_question_set_from_db,
    update_question_set_in_db,
)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.services.logging_service import logger


def test_create_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    assert question_set.name == test_schema_question_set.name
    assert question_set.description == test_schema_question_set.description
    assert question_set.is_public == test_schema_question_set.is_public


def test_read_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    read_set = read_question_set_from_db(db_session, question_set.id)
    assert read_set.id == question_set.id
    assert read_set.name == question_set.name


def test_read_question_sets(db_session, test_schema_question_set):
    create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question_sets = read_question_sets_from_db(db_session)
    assert len(question_sets) > 0


def test_update_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    updated_data = {
        "name": "Updated Question Set",
        "description": "Updated description",
    }
    updated_set = update_question_set_in_db(db_session, question_set.id, updated_data)
    assert updated_set.name == "Updated Question Set"
    assert updated_set.description == "Updated description"


def test_delete_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    assert delete_question_set_from_db(db_session, question_set.id) is True
    assert read_question_set_from_db(db_session, question_set.id) is None


def test_create_question_set_to_question_association(
    db_session, test_schema_question_set, test_schema_question
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert (
        create_question_set_to_question_association_in_db(
            db_session, question_set.id, question.id
        )
        is True
    )


def test_delete_question_set_to_question_association(
    db_session, test_schema_question_set, test_schema_question
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_set_to_question_association_in_db(
        db_session, question_set.id, question.id
    )
    assert (
        delete_question_set_to_question_association_from_db(
            db_session, question_set.id, question.id
        )
        is True
    )


def test_create_question_set_to_group_association(
    db_session, test_schema_question_set, test_schema_group
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    assert (
        create_question_set_to_group_association_in_db(
            db_session, question_set.id, group.id
        )
        is True
    )


def test_delete_question_set_to_group_association(
    db_session, test_schema_question_set, test_schema_group
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    create_question_set_to_group_association_in_db(
        db_session, question_set.id, group.id
    )
    assert (
        delete_question_set_to_group_association_from_db(
            db_session, question_set.id, group.id
        )
        is True
    )


def test_read_questions_for_question_set(
    db_session, test_schema_question_set, test_schema_question
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_set_to_question_association_in_db(
        db_session, question_set.id, question.id
    )
    questions = read_questions_for_question_set_from_db(db_session, question_set.id)
    assert len(questions) == 1
    assert questions[0].id == question.id


def test_read_groups_for_question_set(
    db_session, test_schema_question_set, test_schema_group
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    create_question_set_to_group_association_in_db(
        db_session, question_set.id, group.id
    )
    groups = read_groups_for_question_set_from_db(db_session, question_set.id)
    assert len(groups) == 1
    assert groups[0].id == group.id


def test_create_question_set_with_duplicate_name(db_session, test_schema_question_set):
    create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    with pytest.raises(
        ValueError, match="A question set with this name already exists for this user"
    ):
        create_question_set_in_db(db_session, test_schema_question_set.model_dump())


def test_read_nonexistent_question_set(db_session):
    nonexistent_id = 9999
    assert read_question_set_from_db(db_session, nonexistent_id) is None


def test_update_nonexistent_question_set(db_session):
    nonexistent_id = 9999
    updated_data = {"name": "Updated Question Set"}
    with pytest.raises(ValueError, match="Question set with id 9999 does not exist"):
        update_question_set_in_db(db_session, nonexistent_id, updated_data)


def test_delete_nonexistent_question_set(db_session):
    nonexistent_id = 9999
    assert delete_question_set_from_db(db_session, nonexistent_id) is False


def test_create_question_set_with_questions(
    db_session, test_schema_question_set, test_schema_question
):
    question1 = create_question_in_db(db_session, test_schema_question.model_dump())
    logger.debug("question1: %s", question1)
    question2 = create_question_in_db(
        db_session, {**test_schema_question.model_dump(), "text": "Another question"}
    )
    logger.debug("question2: %s", question2)

    question_set_data = test_schema_question_set.model_dump()
    question_set_data["question_ids"] = [question1.id, question2.id]
    logger.debug("question_set_data: %s", question_set_data)

    question_set = create_question_set_in_db(db_session, question_set_data)
    logger.debug("question_set: %s", question_set)

    questions = read_questions_for_question_set_from_db(db_session, question_set.id)
    logger.debug("questions: %s", questions)
    assert len(questions) == 2
    assert {q.id for q in questions} == {question1.id, question2.id}


def test_update_question_set_questions(
    db_session, test_schema_question_set, test_schema_question
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    question1 = create_question_in_db(db_session, test_schema_question.model_dump())
    question2 = create_question_in_db(
        db_session, {**test_schema_question.model_dump(), "text": "Another question"}
    )

    update_data = {"question_ids": [question1.id, question2.id]}
    updated_set = update_question_set_in_db(db_session, question_set.id, update_data)

    questions = read_questions_for_question_set_from_db(db_session, updated_set.id)
    assert len(questions) == 2
    assert {q.id for q in questions} == {question1.id, question2.id}


def test_read_question_sets_pagination(db_session, test_schema_question_set):
    for i in range(5):
        create_question_set_in_db(
            db_session,
            {**test_schema_question_set.model_dump(), "name": f"Question Set {i}"},
        )

    page1 = read_question_sets_from_db(db_session, skip=0, limit=2)
    page2 = read_question_sets_from_db(db_session, skip=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


def test_delete_question_set_cascading(
    db_session, test_schema_question_set, test_schema_question, test_schema_group
):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())

    create_question_set_to_question_association_in_db(
        db_session, question_set.id, question.id
    )
    create_question_set_to_group_association_in_db(
        db_session, question_set.id, group.id
    )

    delete_question_set_from_db(db_session, question_set.id)

    assert read_question_set_from_db(db_session, question_set.id) is None
    assert read_questions_for_question_set_from_db(db_session, question_set.id) == []
    assert read_groups_for_question_set_from_db(db_session, question_set.id) == []


def test_create_question_set_with_invalid_question_id(
    db_session, test_schema_question_set
):
    question_set_data = test_schema_question_set.model_dump()
    question_set_data["question_ids"] = [9999]  # Non-existent question ID
    logger.debug("question_set_data: %s", question_set_data)

    with pytest.raises(ValueError) as exc_info:
        created_question_set = create_question_set_in_db(db_session, question_set_data)
        logger.debug("created_question_set: %s", created_question_set)
    assert "Question with id 9999 does not exist" in str(exc_info.value)


def test_create_question_set_with_invalid_group_id(
    db_session, test_schema_question_set
):
    question_set_data = test_schema_question_set.model_dump()
    question_set_data["group_ids"] = [9999]  # Non-existent group ID
    logger.debug("question_set_data: %s", question_set_data)

    with pytest.raises(ValueError) as exc_info:
        created_question_set = create_question_set_in_db(db_session, question_set_data)
        logger.debug("created_question_set: %s", created_question_set)
    assert "Group with id 9999 does not exist" in str(exc_info.value)


def test_update_question_set_toggle_public(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(
        db_session, test_schema_question_set.model_dump()
    )
    original_is_public = question_set.is_public

    update_data = {"is_public": not original_is_public}
    updated_set = update_question_set_in_db(db_session, question_set.id, update_data)

    assert updated_set.is_public != original_is_public
