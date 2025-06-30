# filename: backend/tests/fixtures/integration/complex_data_fixtures.py

import pytest

from backend.app.crud.crud_concepts import create_concept_in_db
from backend.tests.helpers.fixture_performance import track_fixture_performance
from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db
from backend.app.crud.crud_topics import create_topic_in_db
from backend.app.models.questions import DifficultyLevel
from backend.app.schemas.concepts import ConceptCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema
from backend.app.schemas.questions import QuestionCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.topics import TopicCreateSchema


@pytest.fixture(scope="function")  
@track_fixture_performance(scope="function")
def setup_filter_questions_data(db_session, test_model_user_with_group, session_reference_content_hierarchy):
    """Create a comprehensive dataset for testing question filtering functionality.
    
    This fixture now builds on session-scoped reference data, creating only
    test-specific content (tags, question sets, questions) rather than the
    entire content hierarchy.
    """
    # Use session-scoped reference content hierarchy
    hierarchy = session_reference_content_hierarchy
    
    # Extract reference data for easy access
    domains = hierarchy["domains"]
    disciplines = hierarchy["disciplines"] 
    subjects = hierarchy["subjects"]
    topics = hierarchy["topics"]
    subtopics = hierarchy["subtopics"]
    concepts = hierarchy["concepts"]

    # Create only test-specific content: Tags
    tag1 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="physics").model_dump()
    )
    tag2 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="mathematics").model_dump()
    )
    tag3 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="mechanics").model_dump()
    )
    tag4 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="linear algebra").model_dump()
    )

    # Create Question Sets
    question_set1 = create_question_set_in_db(
        db_session,
        QuestionSetCreateSchema(
            name="Physics Question Set",
            is_public=True,
            creator_id=test_model_user_with_group.id,
        ).model_dump(),
    )
    question_set2 = create_question_set_in_db(
        db_session,
        QuestionSetCreateSchema(
            name="Math Question Set",
            is_public=True,
            creator_id=test_model_user_with_group.id,
        ).model_dump(),
    )

    # Create Questions using session reference data IDs
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject_ids=[subjects["classical_mechanics"]["id"]],
            topic_ids=[topics["newtons_laws"]["id"]],
            subtopic_ids=[subtopics["first_law"]["id"]],
            concept_ids=[concepts["inertia"]["id"]],
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="How does force relate to acceleration according to Newton's Second Law?",
            subject_ids=[subjects["classical_mechanics"]["id"]],
            topic_ids=[topics["newtons_laws"]["id"]],
            subtopic_ids=[subtopics["second_law"]["id"]],
            concept_ids=[concepts["force_acceleration"]["id"]],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is the result of multiplying a 2x2 identity matrix with any 2x2 matrix?",
            subject_ids=[subjects["algebra"]["id"]],
            topic_ids=[topics["linear_algebra"]["id"]],
            subtopic_ids=[subtopics["matrices"]["id"]],
            concept_ids=[concepts["matrix_operations"]["id"]],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What does it mean for a set of vectors to be linearly independent?",
            subject_ids=[subjects["algebra"]["id"]],
            topic_ids=[topics["linear_algebra"]["id"]],
            subtopic_ids=[subtopics["vector_spaces"]["id"]],
            concept_ids=[concepts["linear_independence"]["id"]],
            difficulty=DifficultyLevel.HARD,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id],
        ).model_dump(),
    )
    
    # Return reference to the session-scoped hierarchy for test use
    return hierarchy


@pytest.fixture(scope="function")
def filter_test_data(
    db_session,
    test_schema_question,
    test_schema_subject,
    test_schema_topic,
    test_schema_subtopic,
    test_schema_question_tag,
):
    """Create a simple dataset for testing basic filtering functionality."""
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())

    question_data = test_schema_question.model_dump()
    question_data.update(
        {
            "subject_ids": [subject.id],
            "topic_ids": [topic.id],
            "subtopic_ids": [subtopic.id],
            "question_tag_ids": [tag.id],
            "difficulty": DifficultyLevel.MEDIUM,
        }
    )
    question = create_question_in_db(db_session, question_data)

    return {
        "subject": subject,
        "topic": topic,
        "subtopic": subtopic,
        "tag": tag,
        "question": question,
    }