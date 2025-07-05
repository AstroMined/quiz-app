# filename: backend/tests/fixtures/models/content_fixtures.py

import pytest

from backend.app.models.domains import DomainModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.topics import TopicModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.concepts import ConceptModel


@pytest.fixture(scope="function")
def test_model_domain(db_session, test_domains):
    """Get a test domain from reference data, properly attached to current session."""
    # Get the first domain from reference data
    domain = test_domains[0]
    # Merge the domain into the current session to avoid DetachedInstanceError
    merged_domain = db_session.merge(domain)
    # Refresh to ensure relationships are properly loaded
    db_session.refresh(merged_domain)
    return merged_domain


@pytest.fixture(scope="function")
def test_model_discipline(db_session, mathematics_discipline):
    """Get mathematics discipline from reference data, properly attached to current session."""
    # Merge the discipline into the current session to avoid DetachedInstanceError
    merged_discipline = db_session.merge(mathematics_discipline)
    # Refresh to ensure relationships are properly loaded
    db_session.refresh(merged_discipline)
    return merged_discipline


@pytest.fixture(scope="function")
def test_model_subject(db_session, algebra_subject):
    """Get algebra subject from reference data, properly attached to current session."""
    # Merge the subject into the current session to avoid DetachedInstanceError
    merged_subject = db_session.merge(algebra_subject)
    # Refresh to ensure relationships are properly loaded
    db_session.refresh(merged_subject)
    return merged_subject


@pytest.fixture(scope="function")
def test_model_topic(db_session, test_model_subject):
    """Create a test topic associated with a subject."""
    import uuid
    unique_name = f"test_topic_{str(uuid.uuid4())[:8]}"
    topic = TopicModel(name=unique_name)
    
    # Re-attach the subject to the current session to avoid DetachedInstanceError
    subject = db_session.merge(test_model_subject)
    topic.subjects.append(subject)
    db_session.add(topic)
    db_session.flush()  # Use flush instead of commit for transaction rollback
    return topic


@pytest.fixture(scope="function")
def test_model_subtopic(db_session, test_model_topic):
    """Create a test subtopic associated with a topic."""
    import uuid
    unique_name = f"test_subtopic_{str(uuid.uuid4())[:8]}"
    subtopic = SubtopicModel(name=unique_name)
    subtopic.topics.append(test_model_topic)
    db_session.add(subtopic)
    db_session.flush()  # Use flush instead of commit for transaction rollback
    return subtopic


@pytest.fixture(scope="function")
def test_model_concept(db_session, test_model_subtopic):
    """Create a test concept associated with a subtopic."""
    import uuid
    unique_name = f"test_concept_{str(uuid.uuid4())[:8]}"
    concept = ConceptModel(name=unique_name)
    concept.subtopics.append(test_model_subtopic)
    db_session.add(concept)
    db_session.flush()  # Use flush instead of commit for transaction rollback
    return concept