# filename: tests/conftest.py
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import string
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.crud import crud_user, crud_questions, crud_question_sets
from app.schemas import UserCreate, QuestionSetCreate, QuestionCreate
from app.models import User, QuestionSet, Question, Subtopic

# Testing database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
def client(db_session):
    def override_get_db():
        print(f"Overriding get_db dependency with test session: {db_session}")
        try:
            yield db_session
        finally:
            print(f"Ending use of test session: {db_session}")

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    del app.dependency_overrides[get_db]
    print("Removed get_db override.")

@pytest.fixture(scope="function")
def random_username():
    return "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture
def test_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="testpassword")
    user = crud_user.create_user(db_session, user_data)
    db_session.commit()  # Commit the changes to the database
    return user

@pytest.fixture
def test_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    question_set = crud_question_sets.create_question_set(db_session, question_set_data)
    return question_set

@pytest.fixture
def test_question(db_session, test_question_set):
    # Create a test subtopic
    subtopic = Subtopic(name="Test Subtopic")
    db_session.add(subtopic)
    db_session.commit()

    question_data = QuestionCreate(text="Test Question", question_set_id=test_question_set.id, subtopic_id=subtopic.id)
    question = crud_questions.create_question(db_session, question_data)
    return question