# filename: backend/tests/fixtures/integration/minimal_fixtures.py

import pytest

from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.models.questions import DifficultyLevel
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema
from backend.app.schemas.questions import QuestionCreateSchema
from backend.tests.helpers.fixture_performance import track_fixture_performance


@pytest.fixture(scope="function")
def minimal_content_data(db_session, session_reference_content_hierarchy):
    """Create minimal test data using only one subject/topic/concept chain."""
    hierarchy = session_reference_content_hierarchy
    
    return {
        "domain": hierarchy["domains"]["science"],
        "discipline": hierarchy["disciplines"]["physics"],
        "subject": hierarchy["subjects"]["classical_mechanics"],
        "topic": hierarchy["topics"]["newtons_laws"],
        "subtopic": hierarchy["subtopics"]["first_law"],
        "concept": hierarchy["concepts"]["inertia"]
    }


@pytest.fixture(scope="function")
@track_fixture_performance(scope="function")
def minimal_question_data(db_session, minimal_content_data, test_model_user_with_group):
    """Create a single question with minimal relationships for lightweight testing."""
    content = minimal_content_data
    
    # Create minimal question tag
    tag = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="minimal_test").model_dump()
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
def moderate_content_data(db_session, session_reference_content_hierarchy):
    """Create moderate test data using physics and math content for relationship testing."""
    hierarchy = session_reference_content_hierarchy
    
    return {
        "physics": {
            "domain": hierarchy["domains"]["science"],
            "discipline": hierarchy["disciplines"]["physics"],
            "subject": hierarchy["subjects"]["classical_mechanics"],
            "topic": hierarchy["topics"]["newtons_laws"],
            "subtopics": [
                hierarchy["subtopics"]["first_law"],
                hierarchy["subtopics"]["second_law"]
            ],
            "concepts": [
                hierarchy["concepts"]["inertia"],
                hierarchy["concepts"]["force_acceleration"]
            ]
        },
        "mathematics": {
            "domain": hierarchy["domains"]["mathematics"],
            "discipline": hierarchy["disciplines"]["pure_mathematics"],
            "subject": hierarchy["subjects"]["algebra"],
            "topic": hierarchy["topics"]["linear_algebra"],
            "subtopics": [
                hierarchy["subtopics"]["matrices"],
                hierarchy["subtopics"]["vector_spaces"]
            ],
            "concepts": [
                hierarchy["concepts"]["matrix_operations"],
                hierarchy["concepts"]["linear_independence"]
            ]
        }
    }


@pytest.fixture(scope="function")
@track_fixture_performance(scope="function")
def moderate_question_data(db_session, moderate_content_data, test_model_user_with_group):
    """Create a small set of questions for relationship testing."""
    content = moderate_content_data
    
    # Create tags
    physics_tag = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="physics").model_dump()
    )
    math_tag = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="mathematics").model_dump()
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