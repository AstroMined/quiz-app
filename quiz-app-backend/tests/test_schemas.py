# filename: tests/test_schemas.py
import pytest
from app.schemas import UserCreate, QuestionCreate

def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123"
    }
    user_schema = UserCreate(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.password == "TestPassword123"

def test_user_create_schema_password_validation():
    user_data = {"username": "testuser", "password": "ValidPassword123"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123"

def test_question_create_schema():
    question_data = {
        "text": "Test question",
        "subtopic_id": 1,
        "question_set_id": 1
    }
    question_schema = QuestionCreate(**question_data)
    assert question_schema.text == "Test question"
    assert question_schema.subtopic_id == 1
    assert question_schema.question_set_id == 1

# Add similar tests for other schemas