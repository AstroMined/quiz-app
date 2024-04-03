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
    create_user,
    create_question,
    create_question_set,
    create_subtopic
)
from app.schemas import (
    UserCreate,
    QuestionSetCreate,
    QuestionCreate,
    AnswerChoiceCreate,
    SubtopicCreate
    )
from app.models import AnswerChoice
from app.core import create_access_token

# Testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base.metadata.create_all(bind=engine)

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
    return "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="TestPassword123!")
    user = create_user(db_session, user_data)
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()

@pytest.fixture(scope="function")
def test_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    question_set = create_question_set(db_session, question_set_data)
    yield question_set
    db_session.delete(question_set)
    db_session.commit()

@pytest.fixture(scope="function")
def test_subtopic(db_session):
    subtopic_data = SubtopicCreate(name="Test Subtopic")
    subtopic = create_subtopic(db=db_session, subtopic=subtopic_data)
    yield subtopic
    db_session.delete(subtopic)
    db_session.commit()

@pytest.fixture(scope="function")
def test_question(db_session, test_question_set, test_subtopic):
    answer_choice_1 = AnswerChoiceCreate(text="Test Answer 1", is_correct=True)
    answer_choice_2 = AnswerChoiceCreate(text="Test Answer 2", is_correct=False)
    question_data = QuestionCreate(
        text="Test Question",
        question_set_id=test_question_set.id,
        subtopic_id=test_subtopic.id,
        answer_choices=[answer_choice_1, answer_choice_2],
        explanation="Test Explanation"
    )
    question = create_question(db_session, question_data)
    yield question
    db_session.delete(question)
    db_session.commit()

@pytest.fixture(scope="function")
def test_token(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    return access_token

@pytest.fixture(scope="function")
def test_answer_choice(db_session, test_question):
    answer_choice = AnswerChoice(text="Test Answer", is_correct=True, question=test_question)
    db_session.add(answer_choice)
    db_session.commit()
    yield answer_choice
    db_session.delete(answer_choice)
    db_session.commit()
