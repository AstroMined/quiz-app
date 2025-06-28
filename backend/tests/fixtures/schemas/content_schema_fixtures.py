# filename: backend/tests/fixtures/schemas/content_schema_fixtures.py

import pytest

from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.topics import TopicCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.concepts import ConceptCreateSchema


@pytest.fixture(scope="function")
def test_schema_domain():
    """Create a test domain creation schema."""
    return DomainCreateSchema(name="test_schema Domain")


@pytest.fixture(scope="function")
def test_schema_discipline(test_model_domain):
    """Create a test discipline creation schema."""
    return DisciplineCreateSchema(
        name="test_schema Discipline", domain_ids=[test_model_domain.id]
    )


@pytest.fixture(scope="function")
def test_schema_subject(test_model_discipline):
    """Create a test subject creation schema."""
    return SubjectCreateSchema(
        name="test_schema Subject", discipline_ids=[test_model_discipline.id]
    )


@pytest.fixture(scope="function")
def test_schema_topic(test_model_subject):
    """Create a test topic creation schema."""
    return TopicCreateSchema(
        name="test_schema Topic", subject_ids=[test_model_subject.id]
    )


@pytest.fixture(scope="function")
def test_schema_subtopic(test_model_topic):
    """Create a test subtopic creation schema."""
    return SubtopicCreateSchema(
        name="test_schema Subtopic", topic_ids=[test_model_topic.id]
    )


@pytest.fixture(scope="function")
def test_schema_concept(test_model_subtopic):
    """Create a test concept creation schema."""
    return ConceptCreateSchema(
        name="test_schema Concept", subtopic_ids=[test_model_subtopic.id]
    )