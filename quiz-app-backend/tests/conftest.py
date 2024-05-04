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
    create_subtopic_crud,
    create_subject_crud,
    create_topic_crud
)
from app.schemas import (
    UserCreateSchema,
    QuestionSetCreateSchema,
    QuestionCreateSchema,
    AnswerChoiceCreateSchema,
    SubtopicCreateSchema,
    SubjectCreateSchema,
    TopicCreateSchema
    )
from app.models import (
    AnswerChoiceModel,
    SubjectModel,
    TopicModel,
    SubtopicModel,
    QuestionModel,
    QuestionTagModel,
    QuestionSetModel
)
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
    yield "test.user_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username):
    email = f"{random_username}@example.com"
    user_data = UserCreateSchema(username=random_username, email=email, password="TestPassword123!")
    user = create_user_crud(db_session, user_data)
    user.is_admin = True
    db_session.add(user)
    db_session.commit()
    yield user

@pytest.fixture
def test_question_set_data(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    return QuestionSetCreateSchema(name="Sample Question Set", subject_id=subject.id)

@pytest.fixture(scope="function")
def test_question_set(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    question_set_data = QuestionSetCreateSchema(name="Test Question Set", subject_id=subject.id)
    question_set = create_question_set_crud(db_session, question_set_data)
    db_session.commit()
    yield question_set

@pytest.fixture(scope="function")
def test_subject(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db=db_session, subject=subject_data)
    yield subject

@pytest.fixture(scope="function")
def test_topic(db_session, test_subject):
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=test_subject.id)
    topic = create_topic_crud(db=db_session, topic=topic_data)
    yield topic

@pytest.fixture(scope="function")
def test_subtopic(db_session, test_topic):
    subtopic_data = SubtopicCreateSchema(name="Test Subtopic", topic_id=test_topic.id)
    subtopic = create_subtopic_crud(db=db_session, subtopic=subtopic_data)
    yield subtopic

@pytest.fixture(scope="function")
def test_question(db_session, test_question_set, test_subtopic, test_topic, test_subject):
    answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True, explanation="Test Explanation 1")
    answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False, explanation="Test Explanation 2")
    question_data = QuestionCreateSchema(
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

@pytest.fixture(scope="function")
def test_token(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    yield access_token

@pytest.fixture(scope="function")
def test_answer_choice_1(db_session, test_question):
    answer_choice = AnswerChoiceModel(text="Test Answer 1", is_correct=True, question=test_question)
    db_session.add(answer_choice)
    db_session.commit()
    yield answer_choice

@pytest.fixture(scope="function")
def test_answer_choice_2(db_session, test_question):
    answer_choice = AnswerChoiceModel(text="Test Answer 2", is_correct=False, question=test_question)
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

@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session):
    # Create multiple subjects, topics, and subtopics
    subject1 = SubjectModel(name="Math")
    subject2 = SubjectModel(name="Science")
    topic1 = TopicModel(name="Algebra", subject=subject1)
    topic2 = TopicModel(name="Geometry", subject=subject1)
    topic3 = TopicModel(name="Physics", subject=subject2)
    subtopic1 = SubtopicModel(name="Linear Equations", topic=topic1)
    subtopic2 = SubtopicModel(name="Quadratic Equations", topic=topic1)
    subtopic3 = SubtopicModel(name="Triangles", topic=topic2)
    subtopic4 = SubtopicModel(name="Mechanics", topic=topic3)
    db_session.add_all([subject1, subject2, topic1, topic2, topic3, subtopic1, subtopic2, subtopic3, subtopic4])
    db_session.commit()

    # Create multiple question tags
    tag1 = QuestionTagModel(tag="equations")
    tag2 = QuestionTagModel(tag="solving")
    tag3 = QuestionTagModel(tag="geometry")
    tag4 = QuestionTagModel(tag="physics")
    db_session.add_all([tag1, tag2, tag3, tag4])
    db_session.commit()

    # Create multiple question sets
    question_set1 = QuestionSetModel(name="Math Question Set", is_public=True)
    question_set2 = QuestionSetModel(name="Science Question Set", is_public=True)
    db_session.add_all([question_set1, question_set2])
    db_session.commit()

    # Create multiple questions with different filter criteria
    question1 = QuestionModel(
        text="What is x if 2x + 5 = 11?",
        subject=subject1,
        topic=topic1,
        subtopic=subtopic1,
        difficulty="Easy",
        tags=[tag1, tag2]
    )
    question2 = QuestionModel(
        text="Find the roots of the equation: x^2 - 5x + 6 = 0",
        subject=subject1,
        topic=topic1,
        subtopic=subtopic2,
        difficulty="Medium",
        tags=[tag1, tag2]
    )
    question3 = QuestionModel(
        text="Calculate the area of a right-angled triangle with base 4 cm and height 3 cm.",
        subject=subject1,
        topic=topic2,
        subtopic=subtopic3,
        difficulty="Easy",
        tags=[tag3]
    )
    question4 = QuestionModel(
        text="A car accelerates from rest at 2 m/s^2. What is its velocity after 5 seconds?",
        subject=subject2,
        topic=topic3,
        subtopic=subtopic4,
        difficulty="Medium",
        tags=[tag4]
    )
    db_session.add_all([question1, question2, question3, question4])
    db_session.commit()
