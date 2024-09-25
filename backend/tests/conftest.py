# filename: backend/tests/conftest.py

import os
import random
import string
import sys
from datetime import datetime, timezone

import pytest
import toml
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.jwt import create_access_token
from backend.app.core.security import get_password_hash
from backend.app.crud.crud_concepts import create_concept_in_db
from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db
from backend.app.crud.crud_time_period import init_time_periods_in_db
from backend.app.crud.crud_topics import create_topic_in_db
from backend.app.db.base import Base
from backend.app.main import app
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.concepts import ConceptModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.models.groups import GroupModel
from backend.app.models.permissions import PermissionModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.roles import RoleModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.models.users import UserModel
from backend.app.schemas.answer_choices import AnswerChoiceCreateSchema
from backend.app.schemas.concepts import ConceptCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.groups import GroupCreateSchema
from backend.app.schemas.leaderboard import LeaderboardCreateSchema
from backend.app.schemas.permissions import PermissionCreateSchema
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema
from backend.app.schemas.questions import (
    QuestionCreateSchema,
    QuestionWithAnswersCreateSchema,
)
from backend.app.schemas.roles import RoleCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.topics import TopicCreateSchema
from backend.app.schemas.user import UserCreateSchema
from backend.app.schemas.user_responses import UserResponseCreateSchema
from backend.app.services.logging_service import logger
from backend.app.services.permission_generator_service import (
    ensure_permissions_in_db,
    generate_permissions,
)

# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Set the environment to test for pytest
os.environ["ENVIRONMENT"] = "test"

# Load the test database URL from pyproject.toml
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pyproject.toml"
)
config = toml.load(config_path)
SQLALCHEMY_TEST_DATABASE_URL = config["tool"]["app"]["database_url_test"]


@pytest.fixture(autouse=True)
def log_test_name(request):
    logger.debug("Running test: %s", request.node.nodeid)
    yield
    logger.debug("Finished test: %s", request.node.nodeid)


def reset_database(db_url):
    engine = create_engine(db_url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    reset_database(SQLALCHEMY_TEST_DATABASE_URL)
    session = TestingSessionLocal()
    session.rollback()  # Roll back any existing transaction
    try:
        init_time_periods_in_db(session)
        yield session
    finally:
        session.close()
        reset_database(SQLALCHEMY_TEST_DATABASE_URL)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[override_get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_permission(db_session):
    permission = PermissionModel(
        name="test_permission", description="A test permission"
    )
    db_session.add(permission)
    db_session.commit()
    return permission


@pytest.fixture(scope="function")
def test_model_permissions(db_session):
    permissions = generate_permissions(app)
    ensure_permissions_in_db(db_session, permissions)
    db_permissions = db_session.query(PermissionModel).all()

    return db_permissions


@pytest.fixture(scope="function")
def test_model_role(db_session, test_model_permissions):
    role = RoleModel(name="test_role", description="Test Role", default=False)
    role.permissions.extend(test_model_permissions)
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)

    return role


@pytest.fixture(scope="function")
def test_model_default_role(db_session, test_model_permissions):
    role = RoleModel(
        name="test_default_role", description="Test Default Role", default=True
    )
    role.permissions.extend(test_model_permissions)
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)

    return role


@pytest.fixture(scope="function")
def test_random_username():
    random_username = "test.user_" + "".join(
        random.choices(string.ascii_letters + string.digits, k=5)
    )
    return random_username.lower()


@pytest.fixture(scope="function")
def test_model_user(db_session, test_random_username, test_model_role):
    email = f"{test_random_username}@example.com"
    hashed_password = get_password_hash("TestPassword123!")

    user = UserModel(
        username=test_random_username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=True,
        role_id=test_model_role.id,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def test_model_group(db_session, test_model_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_model_user.id,
    )
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    return group


@pytest.fixture(scope="function")
def test_model_user_with_group(db_session, test_model_user, test_model_group):
    association = UserToGroupAssociation(
        user_id=test_model_user.id, group_id=test_model_group.id
    )
    db_session.add(association)
    db_session.commit()

    return test_model_user


@pytest.fixture(scope="function")
def test_model_tag(db_session):
    tag = QuestionTagModel(tag="Test Tag")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)

    return tag


@pytest.fixture(scope="function")
def test_model_question_set(db_session, test_model_user_with_group):
    question_set = QuestionSetModel(
        name="Test Question Set",
        is_public=True,
        creator_id=test_model_user_with_group.id,
    )
    db_session.add(question_set)
    db_session.commit()
    db_session.refresh(question_set)

    return question_set


@pytest.fixture(scope="function")
def test_model_answer_choices(db_session):
    answer_choices = [
        AnswerChoiceModel(
            text="Answer 1 for Q1", is_correct=True, explanation="Explanation 1 for Q1"
        ),
        AnswerChoiceModel(
            text="Answer 2 for Q1", is_correct=False, explanation="Explanation 2 for Q1"
        ),
        AnswerChoiceModel(
            text="Answer 1 for Q2", is_correct=True, explanation="Explanation 1 for Q2"
        ),
        AnswerChoiceModel(
            text="Answer 2 for Q2", is_correct=False, explanation="Explanation 2 for Q2"
        ),
    ]

    for answer_choice in answer_choices:
        db_session.add(answer_choice)
    db_session.commit()

    return answer_choices


@pytest.fixture(scope="function")
def test_model_domain(db_session):
    domain = DomainModel(name="Test Domain")
    db_session.add(domain)
    db_session.commit()

    return domain


@pytest.fixture(scope="function")
def test_model_discipline(db_session, test_model_domain):
    discipline = DisciplineModel(name="Test Discipline")
    discipline.domains.append(test_model_domain)
    db_session.add(discipline)
    db_session.commit()

    return discipline


@pytest.fixture(scope="function")
def test_model_subject(db_session, test_model_discipline):
    subject = SubjectModel(name="Test Subject")
    subject.disciplines.append(test_model_discipline)
    db_session.add(subject)
    db_session.commit()

    return subject


@pytest.fixture(scope="function")
def test_model_topic(db_session, test_model_subject):
    topic = TopicModel(name="Test Topic")
    topic.subjects.append(test_model_subject)
    db_session.add(topic)
    db_session.commit()

    return topic


@pytest.fixture(scope="function")
def test_model_subtopic(db_session, test_model_topic):
    subtopic = SubtopicModel(name="Test Subtopic")
    subtopic.topics.append(test_model_topic)
    db_session.add(subtopic)
    db_session.commit()

    return subtopic


@pytest.fixture(scope="function")
def test_model_concept(db_session, test_model_subtopic):
    concept = ConceptModel(name="Test Concept")
    concept.subtopics.append(test_model_subtopic)
    db_session.add(concept)
    db_session.commit()

    return concept


@pytest.fixture(scope="function")
def test_model_questions(
    db_session,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
    test_model_answer_choices,
):
    questions = []
    for i in range(2):
        question = QuestionModel(
            text=f"Test Question {i+1}",
            difficulty="EASY",
            subjects=[test_model_subject],
            topics=[test_model_topic],
            subtopics=[test_model_subtopic],
            concepts=[test_model_concept],
        )
        db_session.add(question)
        db_session.flush()  # Flush to get the question ID

        # Associate answer choices with the question
        question.answer_choices.extend(test_model_answer_choices[i * 2 : (i + 1) * 2])
        questions.append(question)

    db_session.commit()

    return questions


@pytest.fixture(scope="function")
def test_token(test_model_user):
    access_token = create_access_token(data={"sub": test_model_user.username})
    return access_token


@pytest.fixture(scope="function")
def logged_in_client(client, test_model_user_with_group):
    login_data = {
        "username": test_model_user_with_group.username,
        "password": "TestPassword123!",
    }
    response = client.post("/login", json=login_data)
    logger.debug(response.json())
    access_token = response.json()["access_token"]
    assert response.status_code == 200, "Authentication failed."

    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session, test_model_user_with_group):
    # Create Domains
    domain1 = create_domain_in_db(
        db_session, DomainCreateSchema(name="Science").model_dump()
    )
    domain2 = create_domain_in_db(
        db_session, DomainCreateSchema(name="Mathematics").model_dump()
    )

    # Create Disciplines
    discipline1 = create_discipline_in_db(
        db_session,
        DisciplineCreateSchema(name="Physics", domain_ids=[domain1.id]).model_dump(),
    )
    discipline2 = create_discipline_in_db(
        db_session,
        DisciplineCreateSchema(
            name="Pure Mathematics", domain_ids=[domain2.id]
        ).model_dump(),
    )

    # Create Subjects
    subject1 = create_subject_in_db(
        db_session,
        SubjectCreateSchema(
            name="Classical Mechanics", discipline_ids=[discipline1.id]
        ).model_dump(),
    )
    subject2 = create_subject_in_db(
        db_session,
        SubjectCreateSchema(
            name="Algebra", discipline_ids=[discipline2.id]
        ).model_dump(),
    )

    # Create Topics
    topic1 = create_topic_in_db(
        db_session,
        TopicCreateSchema(name="Newton's Laws", subject_ids=[subject1.id]).model_dump(),
    )
    topic2 = create_topic_in_db(
        db_session,
        TopicCreateSchema(
            name="Linear Algebra", subject_ids=[subject2.id]
        ).model_dump(),
    )

    # Create Subtopics
    subtopic1 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name="First Law of Motion", topic_ids=[topic1.id]
        ).model_dump(),
    )
    subtopic2 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name="Second Law of Motion", topic_ids=[topic1.id]
        ).model_dump(),
    )
    subtopic3 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(name="Matrices", topic_ids=[topic2.id]).model_dump(),
    )
    subtopic4 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(name="Vector Spaces", topic_ids=[topic2.id]).model_dump(),
    )

    # Create Concepts
    concept1 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(name="Inertia", subtopic_ids=[subtopic1.id]).model_dump(),
    )
    concept2 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name="Force and Acceleration", subtopic_ids=[subtopic2.id]
        ).model_dump(),
    )
    concept3 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name="Matrix Operations", subtopic_ids=[subtopic3.id]
        ).model_dump(),
    )
    concept4 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name="Linear Independence", subtopic_ids=[subtopic4.id]
        ).model_dump(),
    )

    # Create Tags
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

    # Create Questions
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject_ids=[subject1.id],
            topic_ids=[topic1.id],
            subtopic_ids=[subtopic1.id],
            concept_ids=[concept1.id],
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="How does force relate to acceleration according to Newton's Second Law?",
            subject_ids=[subject1.id],
            topic_ids=[topic1.id],
            subtopic_ids=[subtopic2.id],
            concept_ids=[concept2.id],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is the result of multiplying a 2x2 identity matrix with any 2x2 matrix?",
            subject_ids=[subject2.id],
            topic_ids=[topic2.id],
            subtopic_ids=[subtopic3.id],
            concept_ids=[concept3.id],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What does it mean for a set of vectors to be linearly independent?",
            subject_ids=[subject2.id],
            topic_ids=[topic2.id],
            subtopic_ids=[subtopic4.id],
            concept_ids=[concept4.id],
            difficulty=DifficultyLevel.HARD,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id],
        ).model_dump(),
    )


@pytest.fixture(scope="function")
def filter_test_data(
    db_session,
    test_schema_question,
    test_schema_subject,
    test_schema_topic,
    test_schema_subtopic,
    test_schema_question_tag,
):
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


@pytest.fixture(scope="function")
def test_schema_answer_choice():
    return AnswerChoiceCreateSchema(
        text="test_schema answer choice",
        is_correct=True,
        explanation="This is a test explanation",
    )


@pytest.fixture(scope="function")
def test_schema_domain():
    return DomainCreateSchema(name="test_schema Domain")


@pytest.fixture(scope="function")
def test_schema_discipline(test_model_domain):
    return DisciplineCreateSchema(
        name="test_schema Discipline", domain_ids=[test_model_domain.id]
    )


@pytest.fixture(scope="function")
def test_schema_subject(test_model_discipline):
    return SubjectCreateSchema(
        name="test_schema Subject", discipline_ids=[test_model_discipline.id]
    )


@pytest.fixture(scope="function")
def test_schema_topic(test_model_subject):
    return TopicCreateSchema(
        name="test_schema Topic", subject_ids=[test_model_subject.id]
    )


@pytest.fixture(scope="function")
def test_schema_subtopic(test_model_topic):
    return SubtopicCreateSchema(
        name="test_schema Subtopic", topic_ids=[test_model_topic.id]
    )


@pytest.fixture(scope="function")
def test_schema_concept(test_model_subtopic):
    return ConceptCreateSchema(
        name="test_schema Concept", subtopic_ids=[test_model_subtopic.id]
    )


@pytest.fixture(scope="function")
def test_schema_question(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    return QuestionCreateSchema(
        text="test_schema question",
        difficulty="Medium",
        subject_ids=[test_model_subject.id],
        topic_ids=[test_model_topic.id],
        subtopic_ids=[test_model_subtopic.id],
        concept_ids=[test_model_concept.id],
    )


@pytest.fixture(scope="function")
def test_schema_question_with_answers(test_schema_question, test_schema_answer_choice):
    question_with_answers = test_schema_question.model_dump()
    question_with_answers["answer_choices"] = [test_schema_answer_choice]
    return QuestionWithAnswersCreateSchema(**question_with_answers)


@pytest.fixture(scope="function")
def test_schema_question_set(test_model_user):
    return QuestionSetCreateSchema(
        name="test_schema Question Set",
        description="This is a test question set",
        is_public=True,
        creator_id=test_model_user.id,
    )


@pytest.fixture(scope="function")
def test_schema_question_tag():
    return QuestionTagCreateSchema(tag="test-tag")


@pytest.fixture(scope="function")
def test_schema_user(test_model_role):
    return UserCreateSchema(
        username="testuser",
        email="testuser@example.com",
        password="TestPassword123!",
        role_id=test_model_role.id,
    )


@pytest.fixture(scope="function")
def test_schema_group(test_model_user):
    return GroupCreateSchema(
        name="test_schema Group",
        description="This is a test group",
        creator_id=test_model_user.id,
    )


@pytest.fixture(scope="function")
def test_schema_role(test_model_permissions):
    role_data = {
        "name": "test_schema Role",
        "description": "This is a test role",
        "permissions": [permission.name for permission in test_model_permissions],
    }
    return RoleCreateSchema(**role_data)


@pytest.fixture(scope="function")
def test_schema_permission():
    return PermissionCreateSchema(
        name="test_schema_permission", description="This is a test permission"
    )


@pytest.fixture(scope="function")
def test_schema_leaderboard(test_model_user):
    return LeaderboardCreateSchema(
        user_id=test_model_user.id, score=100, time_period_id=1
    )


@pytest.fixture(scope="function")
def test_schema_user_response(
    test_model_user, test_model_questions, test_model_answer_choices
):
    return UserResponseCreateSchema(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
        response_time=10,
        timestamp=datetime.now(timezone.utc),
    )
