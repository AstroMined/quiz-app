# filename: tests/test_crud.py
import pytest
from app.crud import crud_user, crud_question_sets
from app.schemas import UserCreate, QuestionSetCreate

def test_create_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="NewPassword123")
    created_user = crud_user.create_user(db_session, user_data)
    assert created_user.username == random_username

def test_authenticate_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="AuthPassword123")
    crud_user.create_user(db_session, user_data)
    authenticated_user = crud_user.authenticate_user(db_session, username=random_username, password="AuthPassword123")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    created_question_set = crud_question_sets.create_question_set(db_session, question_set_data)
    assert created_question_set.name == "Test Question Set"

# Add similar tests for other CRUD operations