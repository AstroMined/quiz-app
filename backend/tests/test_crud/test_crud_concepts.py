# filename: backend/tests/crud/test_crud_concepts.py

from backend.app.crud.crud_concepts import (
    create_concept_in_db,
    create_question_to_concept_association_in_db,
    create_subtopic_to_concept_association_in_db,
    delete_concept_from_db,
    delete_question_to_concept_association_from_db,
    delete_subtopic_to_concept_association_from_db,
    read_concept_by_name_from_db,
    read_concept_from_db,
    read_concepts_from_db,
    read_questions_for_concept_from_db,
    read_subtopics_for_concept_from_db,
    update_concept_in_db,
)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db


def test_create_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    assert concept.name == test_schema_concept.name


def test_read_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    read_concept = read_concept_from_db(db_session, concept.id)
    assert read_concept.id == concept.id
    assert read_concept.name == concept.name


def test_read_concept_by_name(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    read_concept = read_concept_by_name_from_db(db_session, concept.name)
    assert read_concept.id == concept.id
    assert read_concept.name == concept.name


def test_read_concepts(db_session, test_schema_concept):
    create_concept_in_db(db_session, test_schema_concept.model_dump())
    concepts = read_concepts_from_db(db_session)
    assert len(concepts) > 0


def test_update_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    updated_data = {"name": "Updated Concept"}
    updated_concept = update_concept_in_db(db_session, concept.id, updated_data)
    assert updated_concept.name == "Updated Concept"


def test_delete_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    assert delete_concept_from_db(db_session, concept.id) is True
    assert read_concept_from_db(db_session, concept.id) is None


def test_create_subtopic_to_concept_association(
    db_session, test_schema_concept, test_schema_subtopic
):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert (
        create_subtopic_to_concept_association_in_db(
            db_session, subtopic.id, concept.id
        )
        is True
    )


def test_delete_subtopic_to_concept_association(
    db_session, test_schema_concept, test_schema_subtopic
):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id)
    assert (
        delete_subtopic_to_concept_association_from_db(
            db_session, subtopic.id, concept.id
        )
        is True
    )


def test_create_question_to_concept_association(
    db_session, test_schema_concept, test_schema_question
):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert (
        create_question_to_concept_association_in_db(
            db_session, question.id, concept.id
        )
        is True
    )


def test_delete_question_to_concept_association(
    db_session, test_schema_concept, test_schema_question
):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_concept_association_in_db(db_session, question.id, concept.id)
    assert (
        delete_question_to_concept_association_from_db(
            db_session, question.id, concept.id
        )
        is True
    )


def test_read_subtopics_for_concept(
    db_session, test_schema_concept, test_schema_subtopic
):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    created_subtopic = create_subtopic_in_db(
        db_session, test_schema_subtopic.model_dump()
    )
    create_subtopic_to_concept_association_in_db(
        db_session, created_subtopic.id, concept.id
    )
    subtopics = read_subtopics_for_concept_from_db(db_session, concept.id)
    assert len(subtopics) == 2
    assert created_subtopic.id in [subtopic.id for subtopic in subtopics]


def test_read_questions_for_concept(
    db_session, test_schema_concept, test_schema_question
):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_concept_association_in_db(db_session, question.id, concept.id)
    questions = read_questions_for_concept_from_db(db_session, concept.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
