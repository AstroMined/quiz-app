#filename: tests/test_crud/conftest.py

from datetime import datetime, timezone
import pytest
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.schemas.domains import DomainCreateSchema
from app.schemas.disciplines import DisciplineCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.topics import TopicCreateSchema
from app.schemas.subtopics import SubtopicCreateSchema
from app.schemas.concepts import ConceptCreateSchema
from app.schemas.questions import QuestionCreateSchema, QuestionWithAnswersCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema
from app.schemas.question_tags import QuestionTagCreateSchema
from app.schemas.user import UserCreateSchema
from app.schemas.groups import GroupCreateSchema
from app.schemas.roles import RoleCreateSchema
from app.schemas.permissions import PermissionCreateSchema
from app.schemas.leaderboard import LeaderboardCreateSchema
from app.schemas.user_responses import UserResponseCreateSchema

from app.crud.crud_subjects import create_subject_in_db
from app.crud.crud_topics import create_topic_in_db
from app.crud.crud_subtopics import create_subtopic_in_db
from app.crud.crud_question_tags import create_question_tag_in_db
from app.crud.crud_questions import create_question_in_db
from app.models.questions import DifficultyLevel

@pytest.fixture
def filter_test_data(db_session, test_schema_question, test_schema_subject, test_schema_topic, test_schema_subtopic, test_schema_question_tag):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())

    question_data = test_schema_question.model_dump()
    question_data.update({
        "subject_ids": [subject.id],
        "topic_ids": [topic.id],
        "subtopic_ids": [subtopic.id],
        "question_tag_ids": [tag.id],
        "difficulty": DifficultyLevel.MEDIUM
    })
    question = create_question_in_db(db_session, question_data)

    return {
        "subject": subject,
        "topic": topic,
        "subtopic": subtopic,
        "tag": tag,
        "question": question
    }

@pytest.fixture(scope="function")
def test_schema_answer_choice():
    return AnswerChoiceCreateSchema(
        text="test_schema answer choice",
        is_correct=True,
        explanation="This is a test explanation"
    )

@pytest.fixture(scope="function")
def test_schema_domain():
    domain = DomainCreateSchema(name="test_schema Domain")
    yield domain

@pytest.fixture(scope="function")
def test_schema_discipline(test_model_domain):
    discipline = DisciplineCreateSchema(
        name="test_schema Discipline",
        domain_ids=[test_model_domain.id]
    )
    yield discipline

@pytest.fixture(scope="function")
def test_schema_subject(test_model_discipline):
    return SubjectCreateSchema(
        name="test_schema Subject",
        discipline_ids=[test_model_discipline.id]
    )

@pytest.fixture(scope="function")
def test_schema_topic(test_model_subject):
    return TopicCreateSchema(
        name="test_schema Topic",
        subject_ids=[test_model_subject.id]
    )

@pytest.fixture(scope="function")
def test_schema_subtopic(test_model_topic):
    return SubtopicCreateSchema(
        name="test_schema Subtopic",
        topic_ids=[test_model_topic.id]
    )

@pytest.fixture(scope="function")
def test_schema_concept(test_model_subtopic):
    return ConceptCreateSchema(
        name="test_schema Concept",
        subtopic_ids=[test_model_subtopic.id]
    )

@pytest.fixture(scope="function")
def test_schema_question(test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question_schema = QuestionCreateSchema(
        text="test_schema question",
        difficulty="Medium",
        subject_ids=[test_model_subject.id],
        topic_ids=[test_model_topic.id],
        subtopic_ids=[test_model_subtopic.id],
        concept_ids=[test_model_concept.id]
    )
    
    yield question_schema

@pytest.fixture(scope="function")
def test_schema_question_with_answers(test_schema_question, test_schema_answer_choice):
    question_with_answers = test_schema_question.model_dump()
    question_with_answers['answer_choices'] = [test_schema_answer_choice]
    question_with_answers_schema = QuestionWithAnswersCreateSchema(**question_with_answers)
    
    yield question_with_answers_schema

@pytest.fixture(scope="function")
def test_schema_question_set(test_model_user):
    return QuestionSetCreateSchema(
        name="test_schema Question Set",
        description="This is a test question set",
        is_public=True,
        creator_id=test_model_user.id
    )

@pytest.fixture(scope="function")
def test_schema_question_tag():
    return QuestionTagCreateSchema(
        tag="test-tag"
    )

@pytest.fixture(scope="function")
def test_schema_user(test_model_role):
    return UserCreateSchema(
        username="testuser",
        email="testuser@example.com",
        password="TestPassword123!",
        role_id=test_model_role.id
    )

@pytest.fixture(scope="function")
def test_schema_group(test_model_user):
    return GroupCreateSchema(
        name="test_schema Group",
        description="This is a test group",
        creator_id=test_model_user.id
    )

@pytest.fixture(scope="function")
def test_schema_role(test_model_permissions):
    role_data = {
        "name": "test_schema Role",
        "description":"This is a test role",
        "permissions": []
    }
    role_data['permissions'].extend(permission.name for permission in test_model_permissions)
    role = RoleCreateSchema(**role_data)

    yield role

@pytest.fixture(scope="function")
def test_schema_permission():
    return PermissionCreateSchema(
        name="test_schema_permission",
        description="This is a test permission"
    )

@pytest.fixture(scope="function")
def test_schema_leaderboard(test_model_user):
    return LeaderboardCreateSchema(
        user_id=test_model_user.id,
        score=100,
        time_period_id=1
    )

@pytest.fixture(scope="function")
def test_schema_user_response(test_model_user, test_model_questions, test_model_answer_choices):
    return UserResponseCreateSchema(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
        response_time=10,
        timestamp=datetime.now(timezone.utc)
    )
