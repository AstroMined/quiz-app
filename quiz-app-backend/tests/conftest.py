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
from app.crud import (
    create_user_crud,
    create_question_crud,
    create_question_set_crud,
    create_subtopic_crud
)
from app.schemas import (
    UserCreateSchema,
    QuestionSetCreateSchema,
    QuestionCreateSchema,
    AnswerChoiceCreateSchema,
    SubtopicCreateSchema
    )
from app.models import AnswerChoiceModel, RevokedTokenModel
from app.core import create_access_token, settings_core

# Testing database
DATABASE_URL = settings_core.DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db):
    yield db

@pytest.fixture(scope="function")
def random_username():
    yield "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username):
    user_data = UserCreateSchema(username=random_username, password="TestPassword123!")
    user = create_user_crud(db_session, user_data)
    user.is_admin = True
    db_session.add(user)
    db_session.commit()
    yield user

@pytest.fixture(scope="function")
def test_question_set(db_session):
    question_set_data = QuestionSetCreateSchema(name="Test Question Set")
    question_set = create_question_set_crud(db_session, question_set_data)
    db_session.commit()
    yield question_set

@pytest.fixture(scope="function")
def test_subtopic(db_session):
    subtopic_data = SubtopicCreateSchema(name="Test Subtopic")
    subtopic = create_subtopic_crud(db=db_session, subtopic=subtopic_data)
    yield subtopic

@pytest.fixture(scope="function")
def test_question(db_session, test_question_set, test_subtopic):
    answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True)
    answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False)
    question_data = QuestionCreateSchema(
        text="Test Question",
        question_set_id=test_question_set.id,
        subtopic_id=test_subtopic.id,
        answer_choices=[answer_choice_1, answer_choice_2],
        explanation="Test Explanation"
    )
    question = create_question_crud(db_session, question_data)
    yield question

@pytest.fixture(scope="function")
def test_token(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    yield access_token

@pytest.fixture(scope="function")
def test_answer_choice(db_session, test_question):
    answer_choice = AnswerChoiceModel(text="Test Answer", is_correct=True, question=test_question)
    db_session.add(answer_choice)
    db_session.commit()
    yield answer_choice

@pytest.fixture(scope="function")
def logged_in_client(client, test_user):
    # Perform login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    access_token = response.json()["access_token"]
    assert response.status_code == 200, "Authentication failed."
    
    # Set Authorization header for subsequent requests
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client
