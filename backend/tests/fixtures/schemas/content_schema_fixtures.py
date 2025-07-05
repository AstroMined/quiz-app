# filename: backend/tests/fixtures/schemas/content_schema_fixtures.py

import pytest
import uuid

from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.topics import TopicCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.concepts import ConceptCreateSchema


@pytest.fixture(scope="function")
def test_schema_domain():
    """Create a test domain creation schema."""
    unique_name = f"test_domain_{str(uuid.uuid4())[:8]}"
    return DomainCreateSchema(name=unique_name)


@pytest.fixture(scope="function")
def test_schema_discipline(test_model_domain):
    """Create a test discipline creation schema."""
    unique_name = f"test_discipline_{str(uuid.uuid4())[:8]}"
    return DisciplineCreateSchema(
        name=unique_name, domain_ids=[test_model_domain.id]
    )


@pytest.fixture(scope="function")
def test_schema_subject(test_model_discipline):
    """Create a test subject creation schema."""
    unique_name = f"test_subject_{str(uuid.uuid4())[:8]}"
    return SubjectCreateSchema(
        name=unique_name, discipline_ids=[test_model_discipline.id]
    )


@pytest.fixture(scope="function")
def test_schema_topic(test_model_subject):
    """Create a test topic creation schema."""
    unique_name = f"test_topic_{str(uuid.uuid4())[:8]}"
    return TopicCreateSchema(
        name=unique_name, subject_ids=[test_model_subject.id]
    )


@pytest.fixture(scope="function")
def test_schema_subtopic(test_model_topic):
    """Create a test subtopic creation schema."""
    unique_name = f"test_subtopic_{str(uuid.uuid4())[:8]}"
    return SubtopicCreateSchema(
        name=unique_name, topic_ids=[test_model_topic.id]
    )


@pytest.fixture(scope="function")
def test_schema_concept(test_model_subtopic):
    """Create a test concept creation schema."""
    unique_name = f"test_concept_{str(uuid.uuid4())[:8]}"
    return ConceptCreateSchema(
        name=unique_name, subtopic_ids=[test_model_subtopic.id]
    )