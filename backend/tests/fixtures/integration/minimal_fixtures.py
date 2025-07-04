# filename: backend/tests/fixtures/integration/minimal_fixtures.py

import pytest
import uuid

from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.models.questions import DifficultyLevel
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema
from backend.app.schemas.questions import QuestionCreateSchema
from backend.tests.helpers.fixture_performance import track_fixture_performance


@pytest.fixture(scope="function")
def minimal_content_data(db_session, test_domains, test_disciplines, test_subjects):
    """Create minimal test data using reference data for base content and test-specific topics/concepts."""
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
    classical_mechanics_subject = next(s for s in test_subjects if s.name == "Classical Mechanics")
    
    # Create test-specific topics, subtopics, concepts with unique names
    topic_name = f"newtons_laws_{str(uuid.uuid4())[:8]}"
    topic = create_topic_in_db(
        db_session,
        TopicCreateSchema(
            name=topic_name,
            subject_ids=[classical_mechanics_subject.id]
        ).model_dump()
    )
    
    subtopic_name = f"first_law_{str(uuid.uuid4())[:8]}"
    subtopic = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=subtopic_name,
            topic_ids=[topic.id]
        ).model_dump()
    )
    
    concept_name = f"inertia_{str(uuid.uuid4())[:8]}"
    concept = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=concept_name,
            subtopic_ids=[subtopic.id]
        ).model_dump()
    )
    
    return {
        "domain": {"id": stem_domain.id, "name": stem_domain.name},
        "discipline": {"id": physics_discipline.id, "name": physics_discipline.name},
        "subject": {"id": classical_mechanics_subject.id, "name": classical_mechanics_subject.name},
        "topic": {"id": topic.id, "name": topic.name},
        "subtopic": {"id": subtopic.id, "name": subtopic.name},
        "concept": {"id": concept.id, "name": concept.name}
    }


@pytest.fixture(scope="function")
@track_fixture_performance(scope="function")
def minimal_question_data(db_session, minimal_content_data, test_model_user_with_group):
    """Create a single question with minimal relationships for lightweight testing."""
    content = minimal_content_data
    
    # Create minimal question tag with unique name
    tag = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag=f"minimal_test_{str(uuid.uuid4())[:8]}").model_dump()
    )
    
    # Create minimal question set
    question_set = create_question_set_in_db(
        db_session,
        QuestionSetCreateSchema(
            name="Minimal Test Set",
            is_public=True,
            creator_id=test_model_user_with_group.id,
        ).model_dump(),
    )
    
    # Create single question
    question = create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is Newton's First Law?",
            subject_ids=[content["subject"]["id"]],
            topic_ids=[content["topic"]["id"]],
            subtopic_ids=[content["subtopic"]["id"]],
            concept_ids=[content["concept"]["id"]],
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag.id],
            question_set_ids=[question_set.id],
        ).model_dump(),
    )
    
    return {
        "question": question,
        "tag": tag,
        "question_set": question_set,
        "content": content
    }


@pytest.fixture(scope="function")
def moderate_content_data(db_session, test_domains, test_disciplines, test_subjects):
    """Create moderate test data using physics and math content for relationship testing."""
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
    physics_topic_name = f"newtons_laws_{str(uuid.uuid4())[:8]}"
    physics_topic = create_topic_in_db(
        db_session,
        TopicCreateSchema(
            name=physics_topic_name,
            subject_ids=[classical_mechanics_subject.id]
        ).model_dump()
    )
    
    physics_subtopic1_name = f"first_law_{str(uuid.uuid4())[:8]}"
    physics_subtopic1 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=physics_subtopic1_name,
            topic_ids=[physics_topic.id]
        ).model_dump()
    )
    
    physics_subtopic2_name = f"second_law_{str(uuid.uuid4())[:8]}"
    physics_subtopic2 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=physics_subtopic2_name,
            topic_ids=[physics_topic.id]
        ).model_dump()
    )
    
    physics_concept1_name = f"inertia_{str(uuid.uuid4())[:8]}"
    physics_concept1 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=physics_concept1_name,
            subtopic_ids=[physics_subtopic1.id]
        ).model_dump()
    )
    
    physics_concept2_name = f"force_acceleration_{str(uuid.uuid4())[:8]}"
    physics_concept2 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=physics_concept2_name,
            subtopic_ids=[physics_subtopic2.id]
        ).model_dump()
    )
    
    # Create test-specific mathematics content
    math_topic_name = f"linear_algebra_{str(uuid.uuid4())[:8]}"
    math_topic = create_topic_in_db(
        db_session,
        TopicCreateSchema(
            name=math_topic_name,
            subject_ids=[algebra_subject.id]
        ).model_dump()
    )
    
    math_subtopic1_name = f"matrices_{str(uuid.uuid4())[:8]}"
    math_subtopic1 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=math_subtopic1_name,
            topic_ids=[math_topic.id]
        ).model_dump()
    )
    
    math_subtopic2_name = f"vector_spaces_{str(uuid.uuid4())[:8]}"
    math_subtopic2 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name=math_subtopic2_name,
            topic_ids=[math_topic.id]
        ).model_dump()
    )
    
    math_concept1_name = f"matrix_operations_{str(uuid.uuid4())[:8]}"
    math_concept1 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=math_concept1_name,
            subtopic_ids=[math_subtopic1.id]
        ).model_dump()
    )
    
    math_concept2_name = f"linear_independence_{str(uuid.uuid4())[:8]}"
    math_concept2 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name=math_concept2_name,
            subtopic_ids=[math_subtopic2.id]
        ).model_dump()
    )
    
    return {
        "physics": {
            "domain": {"id": stem_domain.id, "name": stem_domain.name},
            "discipline": {"id": physics_discipline.id, "name": physics_discipline.name},
            "subject": {"id": classical_mechanics_subject.id, "name": classical_mechanics_subject.name},
            "topic": {"id": physics_topic.id, "name": physics_topic.name},
            "subtopics": [
                {"id": physics_subtopic1.id, "name": physics_subtopic1.name},
                {"id": physics_subtopic2.id, "name": physics_subtopic2.name}
            ],
            "concepts": [
                {"id": physics_concept1.id, "name": physics_concept1.name},
                {"id": physics_concept2.id, "name": physics_concept2.name}
            ]
        },
        "mathematics": {
            "domain": {"id": stem_domain.id, "name": stem_domain.name},
            "discipline": {"id": mathematics_discipline.id, "name": mathematics_discipline.name},
            "subject": {"id": algebra_subject.id, "name": algebra_subject.name},
            "topic": {"id": math_topic.id, "name": math_topic.name},
            "subtopics": [
                {"id": math_subtopic1.id, "name": math_subtopic1.name},
                {"id": math_subtopic2.id, "name": math_subtopic2.name}
            ],
            "concepts": [
                {"id": math_concept1.id, "name": math_concept1.name},
                {"id": math_concept2.id, "name": math_concept2.name}
            ]
        }
    }


@pytest.fixture(scope="function")
@track_fixture_performance(scope="function")
def moderate_question_data(db_session, moderate_content_data, test_model_user_with_group):
    """Create a small set of questions for relationship testing."""
    content = moderate_content_data
    
    # Create tags with unique names
    physics_tag = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag=f"physics_{str(uuid.uuid4())[:8]}").model_dump()
    )
    math_tag = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag=f"mathematics_{str(uuid.uuid4())[:8]}").model_dump()
    )
    
    # Create question sets
    physics_set = create_question_set_in_db(
        db_session,
        QuestionSetCreateSchema(
            name="Physics Test Set",
            is_public=True,
            creator_id=test_model_user_with_group.id,
        ).model_dump(),
    )
    math_set = create_question_set_in_db(
        db_session,
        QuestionSetCreateSchema(
            name="Math Test Set",
            is_public=True,
            creator_id=test_model_user_with_group.id,
        ).model_dump(),
    )
    
    # Create physics question
    physics_question = create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject_ids=[content["physics"]["subject"]["id"]],
            topic_ids=[content["physics"]["topic"]["id"]],
            subtopic_ids=[content["physics"]["subtopics"][0]["id"]],
            concept_ids=[content["physics"]["concepts"][0]["id"]],
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[physics_tag.id],
            question_set_ids=[physics_set.id],
        ).model_dump(),
    )
    
    # Create math question
    math_question = create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is matrix multiplication?",
            subject_ids=[content["mathematics"]["subject"]["id"]],
            topic_ids=[content["mathematics"]["topic"]["id"]],
            subtopic_ids=[content["mathematics"]["subtopics"][0]["id"]],
            concept_ids=[content["mathematics"]["concepts"][0]["id"]],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[math_tag.id],
            question_set_ids=[math_set.id],
        ).model_dump(),
    )
    
    return {
        "questions": [physics_question, math_question],
        "tags": [physics_tag, math_tag],
        "question_sets": [physics_set, math_set],
        "content": content
    }