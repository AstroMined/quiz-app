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
from app.db.base import Base
from app.db.session import get_db, init_db

# CRUD imports
from app.crud.crud_answer_choices import create_answer_choice_crud
from app.crud.crud_user import create_user_crud
from app.crud.crud_question_sets import create_question_set_crud
from app.crud.crud_question_tags import create_question_tag_crud, delete_question_tag_crud
from app.crud.crud_roles import create_role_crud, delete_role_crud
from app.crud.crud_groups import create_group_crud, read_group_crud
from app.crud.crud_domains import create_domain
from app.crud.crud_disciplines import create_discipline
from app.crud.crud_subjects import create_subject
from app.crud.crud_topics import create_topic
from app.crud.crud_subtopics import create_subtopic
from app.crud.crud_concepts import create_concept
from app.crud.crud_questions import create_question, create_question_with_answers

# Schema imports
from app.schemas.user import UserCreateSchema
from app.schemas.groups import GroupCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema
from app.schemas.question_tags import QuestionTagCreateSchema
from app.schemas.questions import QuestionCreateSchema, QuestionWithAnswersCreateSchema
from app.schemas.roles import RoleCreateSchema
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.schemas.domains import DomainCreateSchema
from app.schemas.disciplines import DisciplineCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.topics import TopicCreateSchema
from app.schemas.subtopics import SubtopicCreateSchema
from app.schemas.concepts import ConceptCreateSchema

# Model imports
from app.models.associations import UserToGroupAssociation
from app.models.answer_choices import AnswerChoiceModel
from app.models.authentication import RevokedTokenModel
from app.models.groups import GroupModel
from app.models.leaderboard import LeaderboardModel
from app.models.permissions import PermissionModel
from app.models.question_sets import QuestionSetModel
from app.models.question_tags import QuestionTagModel
from app.models.questions import QuestionModel, DifficultyLevel
from app.models.roles import RoleModel
from app.models.domains import DomainModel
from app.models.disciplines import DisciplineModel
from app.models.subjects import SubjectModel
from app.models.concepts import ConceptModel
from app.models.subtopics import SubtopicModel
from app.models.time_period import TimePeriodModel
from app.models.topics import TopicModel
from app.models.user_responses import UserResponseModel
from app.models.users import UserModel
from app.core.jwt import create_access_token
from app.core.security import get_password_hash
from app.services.permission_generator_service import generate_permissions
from app.services.logging_service import logger, sqlalchemy_obj_to_dict


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
        session.rollback()
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

@pytest.fixture(scope='function')
def test_permission(db_session):
    from app.models.permissions import PermissionModel
    permission = PermissionModel(name="test_permission", description="A test permission")
    db_session.add(permission)
    db_session.commit()
    return permission

@pytest.fixture(scope="function")
def test_permissions(db_session):
    from app.main import app  # Import the actual FastAPI app instance
    from app.services.permission_generator_service import generate_permissions, ensure_permissions_in_db

    # Generate permissions
    permissions = generate_permissions(app)
    
    # Ensure permissions are in the database
    ensure_permissions_in_db(db_session, permissions)

    # Fetch and return the permissions from the database
    db_permissions = db_session.query(PermissionModel).all()
    
    yield db_permissions

    # Clean up (optional, depending on your test isolation needs)
    db_session.query(PermissionModel).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_role(db_session, test_permissions):
    try:
        # Create a test role with all permissions
        role = RoleModel(
            name="test_role",
            description="Test Role",
            default=False
        )
        role.permissions.extend(test_permissions)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        yield role
    except Exception as e:
        logger.exception(f"Error in test_role fixture: {str(e)}")
        raise
    finally:
        logger.debug("Tearing down test_role fixture")
        db_session.rollback()

@pytest.fixture(scope="function")
def random_username():
    yield "test.user_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username, test_role):
    try:
        logger.debug("Setting up test_user fixture")
        email = f"{random_username}@example.com"
        hashed_password = get_password_hash("TestPassword123!")
        
        logger.error(f"Creating test user with role ID: {test_role.id}")
        user = UserModel(
            username=random_username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
            role_id=test_role.id
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        logger.error(f"Created test user: {sqlalchemy_obj_to_dict(user)}")
        yield user
    except Exception as e:
        logger.exception(f"Error in test_user fixture: {str(e)}")
        raise
    finally:
        logger.debug("Tearing down test_user fixture")
        db_session.rollback()

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

@pytest.fixture(scope='function')
def test_question_set_data(db_session, test_user_with_group):
    try:
        logger.debug("Setting up test_question_set_data fixture")
        test_question_set_data_create = {
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
def test_answer_choices(db_session):
    answer_choices = [
        AnswerChoiceModel(text="Answer 1", is_correct=True, explanation="Explanation 1"),
        AnswerChoiceModel(text="Answer 2", is_correct=False, explanation="Explanation 2"),
        AnswerChoiceModel(text="Answer 3", is_correct=False, explanation="Explanation 3"),
        AnswerChoiceModel(text="Answer 4", is_correct=True, explanation="Explanation 4")
    ]
    
    db_answer_choices = []
    for answer_choice in answer_choices:
        db_session.add(answer_choice)
        db_session.commit()
        db_session.refresh(answer_choice)
        db_answer_choices.append(answer_choice)
    
    yield db_answer_choices

@pytest.fixture(scope="function")
def test_questions(db_session, test_subject, test_topic, test_subtopic, test_concept, test_answer_choices):
    try:
        logger.debug("Setting up test_questions fixture")
        question1 = QuestionModel(text="Test Question 1", difficulty=DifficultyLevel.EASY)
        #question1.answer_choices.append([test_answer_choices[0], test_answer_choices[1]])
        question2 = QuestionModel(text="Test Question 2", difficulty=DifficultyLevel.MEDIUM)
        #question2.answer_choices.append([test_answer_choices[2], test_answer_choices[3]])
        questions = [question1, question2]
        
        for question in questions:
            question.subjects.append(test_subject)
            question.topics.append(test_topic)
            question.subtopics.append(test_subtopic)
            question.concepts.append(test_concept)
        
        db_session.add_all(questions)
        db_session.commit()

        yield questions
    except Exception as e:
        logger.exception("Error in test_questions fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_questions fixture")

@pytest.fixture(scope="function")
def test_domain(db_session):
    domain = DomainModel(name="Test Domain")
    yield domain


@pytest.fixture(scope="function")
def test_discipline(db_session, test_domain):
    discipline = DisciplineModel(name="Test Discipline")
    db_session.add(discipline)
    db_session.commit()
    yield discipline


@pytest.fixture(scope="function")
def test_subject(db_session, test_discipline):
    subject = SubjectModel(name="Test Subject")
    subject.disciplines.append(test_discipline)
    db_session.add(subject)
    db_session.commit()
    yield subject


@pytest.fixture(scope="function")
def test_topic(db_session, test_subject):
    topic = TopicModel(name="Test Topic")
    topic.subjects.append(test_subject)
    db_session.add(topic)
    db_session.commit()
    yield topic


@pytest.fixture(scope="function")
def test_subtopic(db_session, test_topic):
    subtopic = SubtopicModel(name="Test Subtopic")
    subtopic.topics.append(test_topic)
    db_session.add(subtopic)
    db_session.commit()
    yield subtopic


@pytest.fixture(scope="function")
def test_concept(db_session, test_subtopic):
    concept = ConceptModel(name="Test Concept")
    concept.subtopics.append(test_subtopic)
    db_session.add(concept)
    db_session.commit()
    yield concept


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

        # Create Domains
        domain1 = create_domain(db_session, DomainCreateSchema(name="Science"))
        domain2 = create_domain(db_session, DomainCreateSchema(name="Mathematics"))

        # Create Disciplines
        discipline1 = create_discipline(db_session, DisciplineCreateSchema(name="Physics", domain=domain1))
        discipline2 = create_discipline(db_session, DisciplineCreateSchema(name="Pure Mathematics", domain=domain2))

        # Create Subjects
        subject1 = create_subject(db_session, SubjectCreateSchema(name="Classical Mechanics", discipline=discipline1))
        subject2 = create_subject(db_session, SubjectCreateSchema(name="Algebra", discipline=discipline2))

        # Create Topics
        topic1 = create_topic(db_session, TopicCreateSchema(name="Newton's Laws", subject=subject1))
        topic2 = create_topic(db_session, TopicCreateSchema(name="Linear Algebra", subject=subject2))

        # Create Subtopics
        subtopic1 = create_subtopic(db_session, SubtopicCreateSchema(name="First Law of Motion", topic=topic1))
        subtopic2 = create_subtopic(db_session, SubtopicCreateSchema(name="Second Law of Motion", topic=topic1))
        subtopic3 = create_subtopic(db_session, SubtopicCreateSchema(name="Matrices", topic=topic2))
        subtopic4 = create_subtopic(db_session, SubtopicCreateSchema(name="Vector Spaces", topic=topic2))

        # Create Concepts
        concept1 = create_concept(db_session, ConceptCreateSchema(name="Inertia", subtopic=subtopic1))
        concept2 = create_concept(db_session, ConceptCreateSchema(name="Force and Acceleration", subtopic=subtopic2))
        concept3 = create_concept(db_session, ConceptCreateSchema(name="Matrix Operations", subtopic=subtopic3))
        concept4 = create_concept(db_session, ConceptCreateSchema(name="Linear Independence", subtopic=subtopic4))

        # Create Tags
        tag1 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="physics"))
        tag2 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="mathematics"))
        tag3 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="mechanics"))
        tag4 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="linear algebra"))

        # Create Question Sets
        question_set1 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Physics Question Set", is_public=True))
        question_set2 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Math Question Set", is_public=True))

        # Create Questions
        question1 = create_question(db_session, QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject=subject1,
            topic=topic1,
            subtopic=subtopic1,
            concept=concept1,
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ))
        question2 = create_question(db_session, QuestionCreateSchema(
            text="How does force relate to acceleration according to Newton's Second Law?",
            subject=subject1,
            topic=topic1,
            subtopic=subtopic2,
            concept=concept2,
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ))
        question3 = create_question(db_session, QuestionCreateSchema(
            text="What is the result of multiplying a 2x2 identity matrix with any 2x2 matrix?",
            subject=subject2,
            topic=topic2,
            subtopic=subtopic3,
            concept=concept3,
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id]
        ))
        question4 = create_question(db_session, QuestionCreateSchema(
            text="What does it mean for a set of vectors to be linearly independent?",
            subject=subject2,
            topic=topic2,
            subtopic=subtopic4,
            concept=concept4,
            difficulty=DifficultyLevel.HARD,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id]
        ))

        logger.debug("Filter questions data setup completed successfully")

    except Exception as e:
        logger.exception("Error in setup_filter_questions_data fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down setup_filter_questions_data fixture")
