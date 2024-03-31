# filename: tests/conftest.py
import sys
sys.path.insert(0, "/code/quiz-app/quiz-app-backend")

# pylint: disable=wrong-import-position
import random
import string
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from app.db import Base, get_db
from app.crud import create_user, create_question, create_question_set
from app.schemas import UserCreate, QuestionSetCreate, QuestionCreate
from app.models import Subtopic
from app.core import create_access_token

# Testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """
    Fixture that creates a test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
def db():
    print("Creating test database and tables...")
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal
    print("Dropping test database tables...")
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db):
    session = db()
    print(f"Starting a new test session: {session}")
    try:
        yield session
        session.commit()
        print("Test session committed.")
    except:
        session.rollback()
        print("Test session rolled back.")
        raise
    finally:
        session.close()
        print(f"Test session closed: {session}")

@pytest.fixture(scope="function")
def random_username():
    return "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture
def test_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="TestPassword123")
    user = create_user(db_session, user_data)
    db_session.commit()
    return user

@pytest.fixture
def test_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    question_set = create_question_set(db_session, question_set_data)
    return question_set

@pytest.fixture
def test_question(db_session, test_question_set):
    # Create a test subtopic
    subtopic = Subtopic(name="Test Subtopic")
    db_session.add(subtopic)
    db_session.commit()

    question_data = QuestionCreate(text="Test Question",
                                   question_set_id=test_question_set.id,
                                   subtopic_id=subtopic.id)
    question = create_question(db_session, question_data)
    return question

@pytest.fixture
def test_token(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    return access_token
