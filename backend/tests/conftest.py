# filename: backend/tests/conftest.py

import os
import sys

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import random
import string

import pytest
import toml
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.jwt import create_access_token
from backend.app.core.security import get_password_hash
from backend.app.crud.crud_answer_choices import create_answer_choice_in_db
from backend.app.crud.crud_concepts import create_concept_in_db
from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_groups import create_group_in_db, read_group_from_db
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_question_tags import (create_question_tag_in_db,
                                                 delete_question_tag_from_db)
from backend.app.crud.crud_questions import \
    create_question_in_db  # , create_question_with_answers
from backend.app.crud.crud_roles import create_role_in_db, delete_role_from_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db
from backend.app.crud.crud_topics import create_topic_in_db
from backend.app.crud.crud_user import create_user_in_db
from backend.app.db.base import Base
from backend.app.db.session import get_db, init_db
from backend.app.main import app
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.concepts import ConceptModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.models.groups import GroupModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.permissions import PermissionModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.roles import RoleModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.models.topics import TopicModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.schemas.answer_choices import AnswerChoiceCreateSchema
from backend.app.schemas.concepts import ConceptCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.groups import GroupCreateSchema
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema
from backend.app.schemas.questions import (QuestionCreateSchema,
                                           QuestionWithAnswersCreateSchema)
from backend.app.schemas.roles import RoleCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.topics import TopicCreateSchema
from backend.app.schemas.user import UserCreateSchema
from backend.app.services.logging_service import logger, sqlalchemy_obj_to_dict
from backend.app.services.permission_generator_service import \
    generate_permissions

# Set the environment to test for pytest
os.environ["ENVIRONMENT"] = "test"

# Load the test database URL from pyproject.toml (now two levels above the current directory)
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pyproject.toml")
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
    from backend.app.models.permissions import PermissionModel
    permission = PermissionModel(name="test_permission", description="A test permission")
    db_session.add(permission)
    db_session.commit()
    return permission

@pytest.fixture(scope="function")
def test_model_permissions(db_session):
    from backend.app.main import app  # Import the actual FastAPI app instance
    from backend.app.services.permission_generator_service import (
        ensure_permissions_in_db, generate_permissions)

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
def test_model_role(db_session, test_model_permissions):
    try:
        # Create a test role with all permissions
        role = RoleModel(
            name="test_role",
            description="Test Role",
            default=False
        )
        role.permissions.extend(test_model_permissions)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        yield role
    except Exception as e:
        raise
    finally:
        logger.debug("Tearing down test_role fixture")
        db_session.rollback()

@pytest.fixture(scope="function")
def random_username():
    yield "test.user_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_model_user(db_session, random_username, test_model_role):
    try:
        email = f"{random_username}@example.com"
        hashed_password = get_password_hash("TestPassword123!")
        
        user = UserModel(
            username=random_username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
            role_id=test_model_role.id
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        yield user
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_group(db_session, test_model_user):
    try:
        group = GroupModel(
            name="Test Group",
            description="This is a test group",
            creator_id=test_model_user.id
        )
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)
        yield group
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_user_with_group(db_session, test_model_user, test_model_group):
    try:
        association = UserToGroupAssociation(user_id=test_model_user.id, group_id=test_model_group.id)
        db_session.add(association)
        db_session.commit()
        yield test_model_user
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_tag(db_session):
    tag = QuestionTagModel(tag="Test Tag")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    yield tag

@pytest.fixture(scope='function')
def test_model_question_set(db_session, test_model_user_with_group):
    try:
        question_set = QuestionSetModel(
            name = "Test Question Set",
            is_public= True,
            creator_id = test_model_user_with_group.id
        )
        db_session.add(question_set)
        db_session.commit()
        db_session.refresh(question_set)
        return question_set
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_answer_choices(db_session):
    answer_choices = [
        AnswerChoiceModel(text="Answer 1 for Q1", is_correct=True, explanation="Explanation 1 for Q1"),
        AnswerChoiceModel(text="Answer 2 for Q1", is_correct=False, explanation="Explanation 2 for Q1"),
        AnswerChoiceModel(text="Answer 1 for Q2", is_correct=True, explanation="Explanation 1 for Q2"),
        AnswerChoiceModel(text="Answer 2 for Q2", is_correct=False, explanation="Explanation 2 for Q2")
    ]
    
    for answer_choice in answer_choices:
        db_session.add(answer_choice)
    db_session.commit()
    
    yield answer_choices

@pytest.fixture(scope="function")
def test_model_domain(db_session):
    domain = DomainModel(name="Test Domain")
    db_session.add(domain)
    db_session.commit()
    yield domain


@pytest.fixture(scope="function")
def test_model_discipline(db_session, test_model_domain):
    discipline = DisciplineModel(name="Test Discipline")
    discipline.domains.append(test_model_domain)
    db_session.add(discipline)
    db_session.commit()
    yield discipline


@pytest.fixture(scope="function")
def test_model_subject(db_session, test_model_discipline):
    subject = SubjectModel(name="Test Subject")
    subject.disciplines.append(test_model_discipline)
    db_session.add(subject)
    db_session.commit()
    yield subject


@pytest.fixture(scope="function")
def test_model_topic(db_session, test_model_subject):
    topic = TopicModel(name="Test Topic")
    topic.subjects.append(test_model_subject)
    db_session.add(topic)
    db_session.commit()
    yield topic


@pytest.fixture(scope="function")
def test_model_subtopic(db_session, test_model_topic):
    subtopic = SubtopicModel(name="Test Subtopic")
    subtopic.topics.append(test_model_topic)
    db_session.add(subtopic)
    db_session.commit()
    yield subtopic


@pytest.fixture(scope="function")
def test_model_concept(db_session, test_model_subtopic):
    concept = ConceptModel(name="Test Concept")
    concept.subtopics.append(test_model_subtopic)
    db_session.add(concept)
    db_session.commit()
    yield concept

@pytest.fixture(scope="function")
def test_model_questions(db_session, test_model_subject, test_model_topic, test_model_subtopic, test_model_concept, test_model_answer_choices):
    try:
        questions = []
        for i in range(2):
            question = QuestionModel(
                text=f"Test Question {i+1}",
                difficulty=DifficultyLevel.EASY,
                subjects=[test_model_subject],
                topics=[test_model_topic],
                subtopics=[test_model_subtopic],
                concepts=[test_model_concept]
            )
            db_session.add(question)
            db_session.flush()  # Flush to get the question ID

            # Associate answer choices with the question
            question.answer_choices.extend(test_model_answer_choices[i*2:(i+1)*2])
            questions.append(question)

        db_session.commit()
        yield questions
    except Exception as e:
        logger.exception("Error in test_questions fixture: %s", str(e))
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_token(test_model_user):
    try:
        logger.debug("Setting up test_token fixture")
        access_token = create_access_token(data={"sub": test_model_user.username})
        yield access_token
    except Exception as e:
        logger.exception("Error in test_token fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_token fixture")

@pytest.fixture(scope="function")
def logged_in_client(client, test_model_user_with_group):
    try:
        logger.debug("Setting up logged_in_client fixture")
        login_data = {"username": test_model_user_with_group.username, "password": "TestPassword123!"}
        logger.debug("Logging in with username: %s", test_model_user_with_group.username)
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
        domain1 = create_domain_in_db(db_session, DomainCreateSchema(name="Science"))
        domain2 = create_domain_in_db(db_session, DomainCreateSchema(name="Mathematics"))

        # Create Disciplines
        discipline1 = create_discipline_in_db(db_session, DisciplineCreateSchema(name="Physics", domain=domain1))
        discipline2 = create_discipline_in_db(db_session, DisciplineCreateSchema(name="Pure Mathematics", domain=domain2))

        # Create Subjects
        subject1 = create_subject_in_db(db_session, SubjectCreateSchema(name="Classical Mechanics", discipline=discipline1))
        subject2 = create_subject_in_db(db_session, SubjectCreateSchema(name="Algebra", discipline=discipline2))

        # Create Topics
        topic1 = create_topic_in_db(db_session, TopicCreateSchema(name="Newton's Laws", subject=subject1))
        topic2 = create_topic_in_db(db_session, TopicCreateSchema(name="Linear Algebra", subject=subject2))

        # Create Subtopics
        subtopic1 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="First Law of Motion", topic=topic1))
        subtopic2 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="Second Law of Motion", topic=topic1))
        subtopic3 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="Matrices", topic=topic2))
        subtopic4 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="Vector Spaces", topic=topic2))

        # Create Concepts
        concept1 = create_concept_in_db(db_session, ConceptCreateSchema(name="Inertia", subtopic=subtopic1))
        concept2 = create_concept_in_db(db_session, ConceptCreateSchema(name="Force and Acceleration", subtopic=subtopic2))
        concept3 = create_concept_in_db(db_session, ConceptCreateSchema(name="Matrix Operations", subtopic=subtopic3))
        concept4 = create_concept_in_db(db_session, ConceptCreateSchema(name="Linear Independence", subtopic=subtopic4))

        # Create Tags
        tag1 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="physics"))
        tag2 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="mathematics"))
        tag3 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="mechanics"))
        tag4 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="linear algebra"))

        # Create Question Sets
        question_set1 = create_question_set_in_db(db_session, QuestionSetCreateSchema(name="Physics Question Set", is_public=True))
        question_set2 = create_question_set_in_db(db_session, QuestionSetCreateSchema(name="Math Question Set", is_public=True))

        # Create Questions
        question1 = create_question_in_db(db_session, QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject=subject1,
            topic=topic1,
            subtopic=subtopic1,
            concept=concept1,
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ))
        question2 = create_question_in_db(db_session, QuestionCreateSchema(
            text="How does force relate to acceleration according to Newton's Second Law?",
            subject=subject1,
            topic=topic1,
            subtopic=subtopic2,
            concept=concept2,
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ))
        question3 = create_question_in_db(db_session, QuestionCreateSchema(
            text="What is the result of multiplying a 2x2 identity matrix with any 2x2 matrix?",
            subject=subject2,
            topic=topic2,
            subtopic=subtopic3,
            concept=concept3,
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id]
        ))
        question4 = create_question_in_db(db_session, QuestionCreateSchema(
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
