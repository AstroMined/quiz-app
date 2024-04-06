# filename: tests/test_crud.py

from app.crud import create_user_crud, create_question_set_crud
from app.schemas import UserCreateSchema, QuestionSetCreateSchema
from app.services import authenticate_user

def test_create_user(db_session, random_username):
    user_data = UserCreateSchema(username=random_username, password="NewPassword123!")
    created_user = create_user_crud(db_session, user_data)
    assert created_user.username == random_username

def test_authenticate_user(db_session, random_username):
    user_data = UserCreateSchema(username=random_username, password="AuthPassword123!")
    create_user_crud(db_session, user_data)
    authenticated_user = authenticate_user(db_session, username=random_username, password="AuthPassword123!")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_question_set(db_session):
    question_set_data = QuestionSetCreateSchema(name="Test CRUD Question Set")
    created_question_set = create_question_set_crud(db_session, question_set_data)
    assert created_question_set.name == "Test CRUD Question Set"

# Add similar tests for other CRUD operations