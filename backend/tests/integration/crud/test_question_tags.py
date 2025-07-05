# filename: backend/tests/test_crud/test_crud_question_tags.py

import pytest
import uuid
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_question_tags import (
    create_question_tag_in_db,
    create_question_to_tag_association_in_db,
    delete_question_tag_from_db,
    delete_question_to_tag_association_from_db,
    read_question_tag_by_tag_from_db,
    read_question_tag_from_db,
    read_question_tags_from_db,
    read_questions_for_tag_from_db,
    read_tags_for_question_from_db,
    update_question_tag_in_db,
)
from backend.app.crud.crud_questions import create_question_in_db


def test_create_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    assert tag.tag == test_schema_question_tag.tag


def test_read_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    read_tag = read_question_tag_from_db(db_session, tag.id)
    assert read_tag.id == tag.id
    assert read_tag.tag == tag.tag


def test_read_question_tag_by_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    read_tag = read_question_tag_by_tag_from_db(db_session, tag.tag)
    assert read_tag.id == tag.id
    assert read_tag.tag == tag.tag


def test_read_question_tags(db_session, test_schema_question_tag):
    create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    tags = read_question_tags_from_db(db_session)
    assert len(tags) > 0


def test_update_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    updated_data = {"tag": "updated-tag"}
    updated_tag = update_question_tag_in_db(db_session, tag.id, updated_data)
    assert updated_tag.tag == "updated-tag"


def test_delete_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    assert delete_question_tag_from_db(db_session, tag.id) is True
    assert read_question_tag_from_db(db_session, tag.id) is None


def test_create_question_to_tag_association(
    db_session, test_schema_question_tag, test_schema_question
):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert (
        create_question_to_tag_association_in_db(db_session, question.id, tag.id)
        is True
    )


def test_delete_question_to_tag_association(
    db_session, test_schema_question_tag, test_schema_question
):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    assert (
        delete_question_to_tag_association_from_db(db_session, question.id, tag.id)
        is True
    )


def test_read_tags_for_question(
    db_session, test_schema_question_tag, test_schema_question
):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    tags = read_tags_for_question_from_db(db_session, question.id)
    assert len(tags) == 1
    assert tags[0].id == tag.id


def test_read_questions_for_tag(
    db_session, test_schema_question_tag, test_schema_question
):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    questions = read_questions_for_tag_from_db(db_session, tag.id)
    assert len(questions) == 1
    assert questions[0].id == question.id


def test_create_duplicate_tag(db_session, test_schema_question_tag):
    create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    with pytest.raises(IntegrityError):
        create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())


def test_read_nonexistent_tag(db_session):
    nonexistent_id = 9999
    assert read_question_tag_from_db(db_session, nonexistent_id) is None


def test_read_nonexistent_tag_by_tag(db_session):
    nonexistent_tag = "nonexistent-tag"
    assert read_question_tag_by_tag_from_db(db_session, nonexistent_tag) is None


def test_update_nonexistent_tag(db_session):
    nonexistent_id = 9999
    updated_data = {"tag": "updated-tag"}
    assert update_question_tag_in_db(db_session, nonexistent_id, updated_data) is None


def test_delete_nonexistent_tag(db_session):
    nonexistent_id = 9999
    assert delete_question_tag_from_db(db_session, nonexistent_id) is False


def test_create_multiple_tags(db_session, test_schema_question_tag):
    tag1 = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    unique_tag = f"another-tag-{str(uuid.uuid4())[:8]}"
    tag2 = create_question_tag_in_db(
        db_session, {**test_schema_question_tag.model_dump(), "tag": unique_tag}
    )
    # Verify both tags were created successfully
    assert tag1.id is not None
    assert tag2.id is not None
    assert tag1.tag != tag2.tag


def test_update_tag_to_existing_name(db_session, test_schema_question_tag):
    tag1 = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    unique_tag = f"another-tag-{str(uuid.uuid4())[:8]}"
    tag2 = create_question_tag_in_db(
        db_session, {**test_schema_question_tag.model_dump(), "tag": unique_tag}
    )
    with pytest.raises(IntegrityError):
        update_question_tag_in_db(db_session, tag2.id, {"tag": tag1.tag})


def test_read_tags_pagination(db_session, test_schema_question_tag):
    for i in range(5):
        create_question_tag_in_db(
            db_session, {**test_schema_question_tag.model_dump(), "tag": f"tag-{i}"}
        )

    page1 = read_question_tags_from_db(db_session, skip=0, limit=2)
    page2 = read_question_tags_from_db(db_session, skip=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


def test_delete_tag_cascading(
    db_session, test_schema_question_tag, test_schema_question
):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)

    delete_question_tag_from_db(db_session, tag.id)

    assert read_question_tag_from_db(db_session, tag.id) is None
    assert read_tags_for_question_from_db(db_session, question.id) == []


def test_create_tag_with_description(db_session, test_schema_question_tag):
    tag_data = test_schema_question_tag.model_dump()
    tag_data["description"] = "This is a test tag description"
    tag = create_question_tag_in_db(db_session, tag_data)
    assert tag.description == "This is a test tag description"


def test_update_tag_description(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    updated_data = {"description": "Updated description"}
    updated_tag = update_question_tag_in_db(db_session, tag.id, updated_data)
    assert updated_tag.description == "Updated description"


def test_create_tag_with_empty_string(db_session, test_schema_question_tag):
    tag_data = test_schema_question_tag.model_dump()
    tag_data["tag"] = ""
    with pytest.raises(ValueError):
        create_question_tag_in_db(db_session, tag_data)


def test_update_tag_to_empty_string(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    with pytest.raises(ValueError):
        update_question_tag_in_db(db_session, tag.id, {"tag": ""})


def test_create_tag_case_insensitive(db_session, test_schema_question_tag):
    create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    # Tags are case-sensitive, so uppercase version should be allowed as different tag
    uppercase_tag = create_question_tag_in_db(
        db_session,
        {
            **test_schema_question_tag.model_dump(),
            "tag": test_schema_question_tag.tag.upper(),
        },
    )
    # Verify both tags exist and are different
    assert uppercase_tag.id is not None
    assert uppercase_tag.tag != test_schema_question_tag.tag
