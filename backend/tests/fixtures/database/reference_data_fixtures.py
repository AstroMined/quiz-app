# filename: backend/tests/fixtures/database/reference_data_fixtures.py

import pytest

from backend.app.crud.crud_concepts import create_concept_in_db
from backend.tests.helpers.fixture_performance import track_fixture_performance
from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db
from backend.app.crud.crud_topics import create_topic_in_db
from backend.app.schemas.concepts import ConceptCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.topics import TopicCreateSchema


@pytest.fixture(scope="session")
@track_fixture_performance(scope="session")
def session_reference_domains(session_factory):
    """Create session-scoped reference domains for test reuse."""
    session = session_factory()
    try:
        # Create base domains
        science_domain = create_domain_in_db(
            session, DomainCreateSchema(name="Science").model_dump()
        )
        math_domain = create_domain_in_db(
            session, DomainCreateSchema(name="Mathematics").model_dump()
        )
        
        session.commit()
        
        # Return IDs and data for cross-session use
        return {
            "science": {"id": science_domain.id, "name": science_domain.name},
            "mathematics": {"id": math_domain.id, "name": math_domain.name}
        }
    finally:
        session.close()


@pytest.fixture(scope="session")
@track_fixture_performance(scope="session")  
def session_reference_disciplines(session_factory, session_reference_domains):
    """Create session-scoped reference disciplines for test reuse."""
    session = session_factory()
    try:
        domains = session_reference_domains
        
        # Create base disciplines
        physics_discipline = create_discipline_in_db(
            session,
            DisciplineCreateSchema(
                name="Physics", 
                domain_ids=[domains["science"]["id"]]
            ).model_dump(),
        )
        math_discipline = create_discipline_in_db(
            session,
            DisciplineCreateSchema(
                name="Pure Mathematics", 
                domain_ids=[domains["mathematics"]["id"]]
            ).model_dump(),
        )
        
        session.commit()
        
        # Return IDs and data for cross-session use
        return {
            "physics": {"id": physics_discipline.id, "name": physics_discipline.name},
            "pure_mathematics": {"id": math_discipline.id, "name": math_discipline.name}
        }
    finally:
        session.close()


@pytest.fixture(scope="session")
@track_fixture_performance(scope="session")
def session_reference_subjects(session_factory, session_reference_disciplines):
    """Create session-scoped reference subjects for test reuse."""
    session = session_factory()
    try:
        disciplines = session_reference_disciplines
        
        # Create base subjects
        mechanics_subject = create_subject_in_db(
            session,
            SubjectCreateSchema(
                name="Classical Mechanics",
                discipline_ids=[disciplines["physics"]["id"]]
            ).model_dump(),
        )
        algebra_subject = create_subject_in_db(
            session,
            SubjectCreateSchema(
                name="Algebra",
                discipline_ids=[disciplines["pure_mathematics"]["id"]]
            ).model_dump(),
        )
        
        session.commit()
        
        # Return IDs and data for cross-session use
        return {
            "classical_mechanics": {"id": mechanics_subject.id, "name": mechanics_subject.name},
            "algebra": {"id": algebra_subject.id, "name": algebra_subject.name}
        }
    finally:
        session.close()


@pytest.fixture(scope="session")
@track_fixture_performance(scope="session")
def session_reference_topics(session_factory, session_reference_subjects):
    """Create session-scoped reference topics for test reuse."""
    session = session_factory()
    try:
        subjects = session_reference_subjects
        
        # Create base topics
        newtons_laws_topic = create_topic_in_db(
            session,
            TopicCreateSchema(
                name="Newton's Laws",
                subject_ids=[subjects["classical_mechanics"]["id"]]
            ).model_dump(),
        )
        linear_algebra_topic = create_topic_in_db(
            session,
            TopicCreateSchema(
                name="Linear Algebra",
                subject_ids=[subjects["algebra"]["id"]]
            ).model_dump(),
        )
        
        session.commit()
        
        # Return IDs and data for cross-session use
        return {
            "newtons_laws": {"id": newtons_laws_topic.id, "name": newtons_laws_topic.name},
            "linear_algebra": {"id": linear_algebra_topic.id, "name": linear_algebra_topic.name}
        }
    finally:
        session.close()


@pytest.fixture(scope="session")
@track_fixture_performance(scope="session")
def session_reference_subtopics(session_factory, session_reference_topics):
    """Create session-scoped reference subtopics for test reuse."""
    session = session_factory()
    try:
        topics = session_reference_topics
        
        # Create base subtopics
        first_law_subtopic = create_subtopic_in_db(
            session,
            SubtopicCreateSchema(
                name="First Law of Motion",
                topic_ids=[topics["newtons_laws"]["id"]]
            ).model_dump(),
        )
        second_law_subtopic = create_subtopic_in_db(
            session,
            SubtopicCreateSchema(
                name="Second Law of Motion",
                topic_ids=[topics["newtons_laws"]["id"]]
            ).model_dump(),
        )
        matrices_subtopic = create_subtopic_in_db(
            session,
            SubtopicCreateSchema(
                name="Matrices",
                topic_ids=[topics["linear_algebra"]["id"]]
            ).model_dump(),
        )
        vector_spaces_subtopic = create_subtopic_in_db(
            session,
            SubtopicCreateSchema(
                name="Vector Spaces",
                topic_ids=[topics["linear_algebra"]["id"]]
            ).model_dump(),
        )
        
        session.commit()
        
        # Return IDs and data for cross-session use
        return {
            "first_law": {"id": first_law_subtopic.id, "name": first_law_subtopic.name},
            "second_law": {"id": second_law_subtopic.id, "name": second_law_subtopic.name},
            "matrices": {"id": matrices_subtopic.id, "name": matrices_subtopic.name},
            "vector_spaces": {"id": vector_spaces_subtopic.id, "name": vector_spaces_subtopic.name}
        }
    finally:
        session.close()


@pytest.fixture(scope="session")
@track_fixture_performance(scope="session")
def session_reference_concepts(session_factory, session_reference_subtopics):
    """Create session-scoped reference concepts for test reuse."""
    session = session_factory()
    try:
        subtopics = session_reference_subtopics
        
        # Create base concepts
        inertia_concept = create_concept_in_db(
            session,
            ConceptCreateSchema(
                name="Inertia",
                subtopic_ids=[subtopics["first_law"]["id"]]
            ).model_dump(),
        )
        force_concept = create_concept_in_db(
            session,
            ConceptCreateSchema(
                name="Force and Acceleration",
                subtopic_ids=[subtopics["second_law"]["id"]]
            ).model_dump(),
        )
        matrix_ops_concept = create_concept_in_db(
            session,
            ConceptCreateSchema(
                name="Matrix Operations",
                subtopic_ids=[subtopics["matrices"]["id"]]
            ).model_dump(),
        )
        linear_independence_concept = create_concept_in_db(
            session,
            ConceptCreateSchema(
                name="Linear Independence",
                subtopic_ids=[subtopics["vector_spaces"]["id"]]
            ).model_dump(),
        )
        
        session.commit()
        
        # Return IDs and data for cross-session use
        return {
            "inertia": {"id": inertia_concept.id, "name": inertia_concept.name},
            "force_acceleration": {"id": force_concept.id, "name": force_concept.name},
            "matrix_operations": {"id": matrix_ops_concept.id, "name": matrix_ops_concept.name},
            "linear_independence": {"id": linear_independence_concept.id, "name": linear_independence_concept.name}
        }
    finally:
        session.close()


@pytest.fixture(scope="session")
def session_reference_content_hierarchy(
    session_reference_domains,
    session_reference_disciplines, 
    session_reference_subjects,
    session_reference_topics,
    session_reference_subtopics,
    session_reference_concepts
):
    """Combine all session-scoped reference content into a single hierarchy."""
    return {
        "domains": session_reference_domains,
        "disciplines": session_reference_disciplines,
        "subjects": session_reference_subjects,
        "topics": session_reference_topics,
        "subtopics": session_reference_subtopics,
        "concepts": session_reference_concepts
    }