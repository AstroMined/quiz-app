# filename: tests/test_crud.py
import pytest
from app.crud import crud_user, crud_question_sets
from app.schemas import UserCreate, QuestionSetCreate

def test_create_user(db_session, random_username):
    username = random_username
    user_data = UserCreate(username=username, password="testpassword")
    created_user = crud_user.create_user(db_session, user_data)
    assert created_user.username == username

def test_create_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    created_question_set = crud_question_sets.create_question_set(db_session, question_set_data)
    assert created_question_set.name == "Test Question Set"

# Add similar tests for other CRUD operations