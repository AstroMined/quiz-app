# filename: tests/conftest.py
import sys
sys.path.insert(0, "/code/quiz-app/quiz-app-backend")

import random
import os
import string
import toml
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base_class import Base
from app.db.session import get_db, init_db
from app.crud.crud_user import create_user_crud
from app.crud.crud_questions import create_question_crud
from app.crud.crud_question_sets import create_question_set_crud
from app.crud.crud_question_tags import create_question_tag_crud, delete_question_tag_crud
from app.crud.crud_roles import create_role_crud, delete_role_crud
from app.crud.crud_subtopics import create_subtopic_crud
from app.crud.crud_subjects import create_subject_crud
from app.crud.crud_topics import create_topic_crud
from app.crud.crud_groups import create_group_crud, read_group_crud
from app.schemas.user import UserCreateSchema
from app.schemas.groups import GroupCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema
from app.schemas.question_tags import QuestionTagCreateSchema
from app.schemas.questions import QuestionCreateSchema
from app.schemas.roles import RoleCreateSchema
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.schemas.subtopics import SubtopicCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.topics import TopicCreateSchema
from app.models.associations import (
    UserToGroupAssociation,
    QuestionSetToGroupAssociation,
    QuestionToTagAssociation,
    QuestionSetToQuestionAssociation,
    RoleToPermissionAssociation
)
from app.models.answer_choices import AnswerChoiceModel
from app.models.authentication import RevokedTokenModel
from app.models.groups import GroupModel
from app.models.leaderboard import LeaderboardModel
from app.models.permissions import PermissionModel
from app.models.question_sets import QuestionSetModel
from app.models.question_tags import QuestionTagModel
from app.models.questions import QuestionModel
from app.models.roles import RoleModel
from app.models.sessions import SessionQuestionModel, SessionQuestionSetModel, SessionModel
from app.models.subjects import SubjectModel
from app.models.subtopics import SubtopicModel
from app.models.time_period import TimePeriodModel
from app.models.topics import TopicModel
from app.models.user_responses import UserResponseModel
from app.models.users import UserModel
from app.core.jwt import create_access_token
from app.services.permission_generator_service import generate_permissions
from app.services.logging_service import logger


# Set the environment to test for pytest
os.environ["ENVIRONMENT"] = "test"

# Load the test database URL from pyproject.toml (one level above the current directory)
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
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

@pytest.fixture(scope='function')
def db_session():
    logger.debug("Begin setting up database fixture")
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    reset_database(SQLALCHEMY_TEST_DATABASE_URL)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        logger.debug("Begin tearing down database fixture")
        session.close()
        reset_database(SQLALCHEMY_TEST_DATABASE_URL)
        logger.debug("Finished tearing down database fixture")

@pytest.fixture(scope='function')
def client(db_session):
    logger.debug("Begin setting up client fixture")
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[override_get_db] = override_get_db
    with TestClient(app) as client:
        logger.debug("Finished setting up client fixture")
        yield client
    app.dependency_overrides.clear()
    logger.debug("Finished tearing down client fixture")

@pytest.fixture
def test_permission(db_session):
    from app.models.permissions import PermissionModel
    permission = PermissionModel(name="test_permission", description="A test permission")
    db_session.add(permission)
    db_session.commit()
    return permission

@pytest.fixture(scope="function")
def test_permissions(db_session):
    from app.main import app  # Import the actual FastAPI app instance
    from app.services.permission_generator_service import generate_permissions

    # Generate permissions
    permissions = generate_permissions(app, db_session)
    
    # Ensure permissions are in the database
    for permission_name in permissions:
        if not db_session.query(PermissionModel).filter_by(name=permission_name).first():
            db_session.add(PermissionModel(name=permission_name))
    db_session.commit()
    
    yield permissions

    # Clean up (optional, depending on your test isolation needs)
    db_session.query(PermissionModel).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_role(db_session, test_permissions):
    # Create a test role with all permissions
    role_data = {
        "name": "test_role",
        "description": "Test Role",
        "permissions": list(test_permissions),
        "default": False
    }
    logger.debug("Creating test role with data: %s", role_data)
    role_create_schema = RoleCreateSchema(**role_data)
    logger.debug("Role create schema: %s", role_create_schema.model_dump())
    role = create_role_crud(db_session, role_create_schema)
    logger.debug("Role created: %s", role)
    yield role

    # Clean up
    delete_role_crud(db_session, role.id)

@pytest.fixture(scope="function")
def random_username():
    yield "test.user_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username, test_role):
    try:
        logger.debug("Setting up test_user fixture")
        email = f"{random_username}@example.com"
        user_data = UserCreateSchema(
            username=random_username,
            email=email,
            password="TestPassword123!",
            role=test_role.name
        )
        user = create_user_crud(db_session, user_data)
        user.is_admin = True
        db_session.add(user)
        db_session.commit()
        yield user
    except Exception as e:
        logger.exception("Error in test_user fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_user fixture")

@pytest.fixture(scope="function")
def test_group(db_session, test_user):
    try:
        logger.debug("Setting up test_group fixture")
        group_data = GroupCreateSchema(
            name="Test Group",
            description="This is a test group",
            creator_id=test_user.id
        )
        group = create_group_crud(db_session, group_data, test_user.id)
        db_session.add(group)
        db_session.commit()
        yield group
    except Exception as e:
        logger.exception("Error in test_group fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_group fixture")
        db_group = read_group_crud(db_session, group.id)
        if db_group:
            db_session.delete(group)
            db_session.commit()

@pytest.fixture(scope="function")
def test_user_with_group(db_session, test_user, test_group):
    try:
        logger.debug("Setting up test_user_with_group fixture")
        association = UserToGroupAssociation(user_id=test_user.id, group_id=test_group.id)
        db_session.add(association)
        db_session.commit()
        yield test_user
    except Exception as e:
        logger.exception("Error in test_user_with_group fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_user_with_group fixture")

@pytest.fixture(scope="function")
def test_tag(db_session):
    tag_data = QuestionTagCreateSchema(tag="Test Tag")
    tag = create_question_tag_crud(db_session, tag_data)
    yield tag
    delete_question_tag_crud(db_session, tag.id)

@pytest.fixture
def test_question_set_data(db_session, test_user_with_group):
    try:
        logger.debug("Setting up test_question_set_data fixture")
        test_question_set_data_create = {
            "db": db_session,
            "name": "Test Question Set",
            "is_public": True,
            "creator_id": test_user_with_group.id
        }
        created_test_question_set_data = QuestionSetCreateSchema(**test_question_set_data_create)
        return created_test_question_set_data
    except Exception as e:
        logger.exception("Error in test_question_set_data fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_question_set_data fixture")

@pytest.fixture(scope="function")
def test_question_set(db_session, test_user, test_question_set_data):
    try:
        logger.debug("Setting up test_question_set fixture")
        question_set = create_question_set_crud(
            db=db_session,
            question_set=test_question_set_data
        )
        db_session.commit()
        yield question_set
    except Exception as e:
        logger.exception("Error in test_question_set fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_question_set fixture")

@pytest.fixture(scope="function")
def test_questions(db_session, test_subject, test_topic, test_subtopic):
    try:
        logger.debug("Setting up test_questions fixture")
        questions_data = [
            QuestionCreateSchema(
                db=db_session,
                text="Test Question 1",
                subject_id=test_subject.id,
                topic_id=test_topic.id,
                subtopic_id=test_subtopic.id,
                difficulty="Easy",
                answer_choices=[
                    AnswerChoiceCreateSchema(text="Answer 1", is_correct=True, explanation="Explanation 1"),
                    AnswerChoiceCreateSchema(text="Answer 2", is_correct=False, explanation="Explanation 2")
                ]
            ),
            QuestionCreateSchema(
                db=db_session,
                text="Test Question 2",
                subject_id=test_subject.id,
                topic_id=test_topic.id,
                subtopic_id=test_subtopic.id,
                difficulty="Medium",
                answer_choices=[
                    AnswerChoiceCreateSchema(text="Answer 3", is_correct=False, explanation="Explanation 3"),
                    AnswerChoiceCreateSchema(text="Answer 4", is_correct=True, explanation="Explanation 4")
                ]
            )
        ]
        questions = [create_question_crud(db_session, q) for q in questions_data]
        yield questions
    except Exception as e:
        logger.exception("Error in test_questions fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_questions fixture")

@pytest.fixture(scope="function")
def test_subject(db_session):
    try:
        logger.debug("Setting up test_subject fixture")
        subject_data = SubjectCreateSchema(name="Test Subject")
        subject = create_subject_crud(db=db_session, subject=subject_data)
        yield subject
    except Exception as e:
        logger.exception("Error in test_subject fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_subject fixture")

@pytest.fixture(scope="function")
def test_topic(db_session, test_subject):
    try:
        logger.debug("Setting up test_topic fixture")
        topic_data = TopicCreateSchema(name="Test Topic", subject_id=test_subject.id)
        topic = create_topic_crud(db=db_session, topic=topic_data)
        yield topic
    except Exception as e:
        logger.exception("Error in test_topic fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_topic fixture")

@pytest.fixture(scope="function")
def test_subtopic(db_session, test_topic):
    try:
        logger.debug("Setting up test_subtopic fixture")
        subtopic_data = SubtopicCreateSchema(name="Test Subtopic", topic_id=test_topic.id)
        subtopic = create_subtopic_crud(db=db_session, subtopic=subtopic_data)
        yield subtopic
    except Exception as e:
        logger.exception("Error in test_subtopic fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_subtopic fixture")

@pytest.fixture(scope="function")
def test_question(db_session, test_question_set, test_subtopic, test_topic, test_subject):
    try:
        logger.debug("Setting up test_question fixture")
        answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True, explanation="Test Explanation 1")
        answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False, explanation="Test Explanation 2")
        question_data = QuestionCreateSchema(
            db=db_session,
            text="Test Question",
            subject_id=test_subject.id,
            topic_id=test_topic.id,
            subtopic_id=test_subtopic.id,
            difficulty="Easy",
            answer_choices=[answer_choice_1, answer_choice_2],
            question_set_ids=[test_question_set.id]
        )
        question = create_question_crud(db_session, question_data)
        yield question
    except Exception as e:
        logger.exception("Error in test_question fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_question fixture")

@pytest.fixture(scope="function")
def test_token(test_user):
    try:
        logger.debug("Setting up test_token fixture")
        access_token = create_access_token(data={"sub": test_user.username})
        yield access_token
    except Exception as e:
        logger.exception("Error in test_token fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_token fixture")

@pytest.fixture(scope="function")
def test_answer_choice_1(db_session, test_question):
    try:
        logger.debug("Setting up test_answer_choice_1 fixture")
        answer_choice = AnswerChoiceModel(text="Test Answer 1", is_correct=True, question=test_question)
        db_session.add(answer_choice)
        db_session.commit()
        yield answer_choice
    except Exception as e:
        logger.exception("Error in test_answer_choice_1 fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_answer_choice_1 fixture")

@pytest.fixture(scope="function")
def test_answer_choice_2(db_session, test_question):
    try:
        logger.debug("Setting up test_answer_choice_2 fixture")
        answer_choice = AnswerChoiceModel(text="Test Answer 2", is_correct=False, question=test_question)
        db_session.add(answer_choice)
        db_session.commit()
        yield answer_choice
    except Exception as e:
        logger.exception("Error in test_answer_choice_2 fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_answer_choice_2 fixture")

@pytest.fixture(scope="function")
def logged_in_client(client, test_user_with_group):
    try:
        logger.debug("Setting up logged_in_client fixture")
        login_data = {"username": test_user_with_group.username, "password": "TestPassword123!"}
        logger.debug("Logging in with username: %s", test_user_with_group.username)
        response = client.post("/login", data=login_data)
        logger.debug("Login response status code: %s", response.status_code)
        access_token = response.json()["access_token"]
        assert response.status_code == 200, "Authentication failed."
        
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        logger.debug("Access token added to client headers")
        yield client
    except Exception as e:
        logger.exception("Error in logged_in_client fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down logged_in_client fixture")

@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session):
    try:
        logger.debug("Setting up filter questions data")

        subject1 = create_subject_crud(db_session, SubjectCreateSchema(name="Math"))
        subject2 = create_subject_crud(db_session, SubjectCreateSchema(name="Science"))

        topic1 = create_topic_crud(db_session, TopicCreateSchema(name="Algebra", subject_id=subject1.id))
        topic2 = create_topic_crud(db_session, TopicCreateSchema(name="Geometry", subject_id=subject1.id))
        topic3 = create_topic_crud(db_session, TopicCreateSchema(name="Physics", subject_id=subject2.id))

        subtopic1 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Linear Equations", topic_id=topic1.id))
        subtopic2 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Quadratic Equations", topic_id=topic1.id))
        subtopic3 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Triangles", topic_id=topic2.id))
        subtopic4 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Mechanics", topic_id=topic3.id))

        tag1 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="equations"))
        tag2 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="solving"))
        tag3 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="geometry"))
        tag4 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="physics"))

        question_set1 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Math Question Set", is_public=True))
        question_set2 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Science Question Set", is_public=True))

        question1 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="What is x if 2x + 5 = 11?",
            subject_id=subject1.id,
            topic_id=topic1.id,
            subtopic_id=subtopic1.id,
            difficulty="Easy",
            tags=[tag1, tag2]
        ))
        question2 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="Find the roots of the equation: x^2 - 5x + 6 = 0",
            subject_id=subject1.id,
            topic_id=topic1.id,
            subtopic_id=subtopic2.id,
            difficulty="Medium",
            tags=[tag1, tag2]
        ))
        question3 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="Calculate the area of a right-angled triangle with base 4 cm and height 3 cm.",
            subject_id=subject1.id,
            topic_id=topic2.id,
            subtopic_id=subtopic3.id,
            difficulty="Easy",
            tags=[tag3]
        ))
        question4 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="A car accelerates from rest at 2 m/s^2. What is its velocity after 5 seconds?",
            subject_id=subject2.id,
            topic_id=topic3.id,
            subtopic_id=subtopic4.id,
            difficulty="Medium",
            tags=[tag4]
        ))

    except Exception as e:
        logger.exception("Error in setup_filter_questions_data fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down setup_filter_questions_data fixture")
