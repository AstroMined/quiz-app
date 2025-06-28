# filename: backend/tests/fixtures/models/content_fixtures.py

import pytest

from backend.app.models.domains import DomainModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.topics import TopicModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.concepts import ConceptModel


@pytest.fixture(scope="function")
def test_model_domain(db_session):
    """Create a test domain."""
    domain = DomainModel(name="Test Domain")
    db_session.add(domain)
    db_session.commit()
    return domain


@pytest.fixture(scope="function")
def test_model_discipline(db_session, test_model_domain):
    """Create a test discipline associated with a domain."""
    discipline = DisciplineModel(name="Test Discipline")
    discipline.domains.append(test_model_domain)
    db_session.add(discipline)
    db_session.commit()
    return discipline


@pytest.fixture(scope="function")
def test_model_subject(db_session, test_model_discipline):
    """Create a test subject associated with a discipline."""
    subject = SubjectModel(name="Test Subject")
    subject.disciplines.append(test_model_discipline)
    db_session.add(subject)
    db_session.commit()
    return subject


@pytest.fixture(scope="function")
def test_model_topic(db_session, test_model_subject):
    """Create a test topic associated with a subject."""
    topic = TopicModel(name="Test Topic")
    topic.subjects.append(test_model_subject)
    db_session.add(topic)
    db_session.commit()
    return topic


@pytest.fixture(scope="function")
def test_model_subtopic(db_session, test_model_topic):
    """Create a test subtopic associated with a topic."""
    subtopic = SubtopicModel(name="Test Subtopic")
    subtopic.topics.append(test_model_topic)
    db_session.add(subtopic)
    db_session.commit()
    return subtopic


@pytest.fixture(scope="function")
def test_model_concept(db_session, test_model_subtopic):
    """Create a test concept associated with a subtopic."""
    concept = ConceptModel(name="Test Concept")
    concept.subtopics.append(test_model_subtopic)
    db_session.add(concept)
    db_session.commit()
    return concept