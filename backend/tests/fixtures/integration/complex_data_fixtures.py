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
def setup_filter_questions_data(db_session, test_model_user_with_group, test_domains, test_disciplines, test_subjects):
    """Create a comprehensive dataset for testing question filtering functionality.
    
    This fixture now builds on session-scoped reference data, creating only
    test-specific content (topics, subtopics, concepts, tags, question sets, questions).
    """
    from backend.app.crud.crud_topics import create_topic_in_db
    from backend.app.crud.crud_subtopics import create_subtopic_in_db
    from backend.app.crud.crud_concepts import create_concept_in_db
    from backend.app.schemas.topics import TopicCreateSchema
    from backend.app.schemas.subtopics import SubtopicCreateSchema
    from backend.app.schemas.concepts import ConceptCreateSchema
    import uuid
    
    # Use reference data for base hierarchy
    stem_domain = next(d for d in test_domains if d.name == "STEM")
    physics_discipline = next(d for d in test_disciplines if d.name == "Physics")
    mathematics_discipline = next(d for d in test_disciplines if d.name == "Mathematics")
    classical_mechanics_subject = next(s for s in test_subjects if s.name == "Classical Mechanics")
    algebra_subject = next(s for s in test_subjects if s.name == "Algebra")
    
    # Create test-specific physics content
    newtons_laws_topic = create_topic_in_db(
        db_session,
        TopicCreateSchema(
            name=f"newtons_laws_{str(uuid.uuid4())[:8]}",
            subject_ids=[classical_mechanics_subject.id]
        ).model_dump()
    )
    
    first_law_subtopic = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=f"first_law_{str(uuid.uuid4())[:8]}",
            topic_ids=[newtons_laws_topic.id]
        ).model_dump()
    )
    
    second_law_subtopic = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=f"second_law_{str(uuid.uuid4())[:8]}",
            topic_ids=[newtons_laws_topic.id]
        ).model_dump()
    )
    
    inertia_concept = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=f"inertia_{str(uuid.uuid4())[:8]}",
            subtopic_ids=[first_law_subtopic.id]
        ).model_dump()
    )
    
    force_acceleration_concept = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=f"force_acceleration_{str(uuid.uuid4())[:8]}",
            subtopic_ids=[second_law_subtopic.id]
        ).model_dump()
    )
    
    # Create test-specific mathematics content
    linear_algebra_topic = create_topic_in_db(
        db_session,
        TopicCreateSchema(
            name=f"linear_algebra_{str(uuid.uuid4())[:8]}",
            subject_ids=[algebra_subject.id]
        ).model_dump()
    )
    
    matrices_subtopic = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=f"matrices_{str(uuid.uuid4())[:8]}",
            topic_ids=[linear_algebra_topic.id]
        ).model_dump()
    )
    
    vector_spaces_subtopic = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=f"vector_spaces_{str(uuid.uuid4())[:8]}",
            topic_ids=[linear_algebra_topic.id]
        ).model_dump()
    )
    
    matrix_operations_concept = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=f"matrix_operations_{str(uuid.uuid4())[:8]}",
            subtopic_ids=[matrices_subtopic.id]
        ).model_dump()
    )
    
    linear_independence_concept = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=f"linear_independence_{str(uuid.uuid4())[:8]}",
            subtopic_ids=[vector_spaces_subtopic.id]
        ).model_dump()
    )
    
    # Create hierarchy dictionary for compatibility with existing code
    hierarchy = {
        "domains": {
            "science": {"id": stem_domain.id, "name": stem_domain.name},
            "mathematics": {"id": stem_domain.id, "name": stem_domain.name}  # Both under STEM now
        },
        "disciplines": {
            "physics": {"id": physics_discipline.id, "name": physics_discipline.name},
            "pure_mathematics": {"id": mathematics_discipline.id, "name": mathematics_discipline.name}
        },
        "subjects": {
            "classical_mechanics": {"id": classical_mechanics_subject.id, "name": classical_mechanics_subject.name},
            "algebra": {"id": algebra_subject.id, "name": algebra_subject.name}
        },
        "topics": {
            "newtons_laws": {"id": newtons_laws_topic.id, "name": newtons_laws_topic.name},
            "linear_algebra": {"id": linear_algebra_topic.id, "name": linear_algebra_topic.name}
        },
        "subtopics": {
            "first_law": {"id": first_law_subtopic.id, "name": first_law_subtopic.name},
            "second_law": {"id": second_law_subtopic.id, "name": second_law_subtopic.name},
            "matrices": {"id": matrices_subtopic.id, "name": matrices_subtopic.name},
            "vector_spaces": {"id": vector_spaces_subtopic.id, "name": vector_spaces_subtopic.name}
        },
        "concepts": {
            "inertia": {"id": inertia_concept.id, "name": inertia_concept.name},
            "force_acceleration": {"id": force_acceleration_concept.id, "name": force_acceleration_concept.name},
            "matrix_operations": {"id": matrix_operations_concept.id, "name": matrix_operations_concept.name},
            "linear_independence": {"id": linear_independence_concept.id, "name": linear_independence_concept.name}
        }
    }
    
    # Extract reference data for easy access (for compatibility)
    domains = hierarchy["domains"]
    disciplines = hierarchy["disciplines"] 
    subjects = hierarchy["subjects"]
    topics = hierarchy["topics"]
    subtopics = hierarchy["subtopics"]
    concepts = hierarchy["concepts"]

    # Create only test-specific content: Tags with unique names
    tag1 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag=f"physics_{str(uuid.uuid4())[:8]}").model_dump()
    )
    tag2 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag=f"mathematics_{str(uuid.uuid4())[:8]}").model_dump()
    )
    tag3 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag=f"mechanics_{str(uuid.uuid4())[:8]}").model_dump()
    )
    tag4 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag=f"linear_algebra_{str(uuid.uuid4())[:8]}").model_dump()
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