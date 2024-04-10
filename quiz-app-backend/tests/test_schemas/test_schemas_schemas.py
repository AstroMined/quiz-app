# filename: tests/test_schemas.py

from app.schemas import UserCreateSchema, QuestionCreateSchema

def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.password == "TestPassword123!"

def test_user_create_schema_password_validation():
    user_data = {"username": "testuser", "password": "ValidPassword123!"}
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_question_create_schema():
    question_data = {
        "text": "Test question",
        "subject_id": 1,
        "topic_id": 1,
        "subtopic_id": 1,
        "question_set_ids": [1],
        "difficulty": "Easy",
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True},
            {"text": "Answer 2", "is_correct": False}
        ],
        "explanation": "Test explanation"
    }
    question_schema = QuestionCreateSchema(**question_data)
    assert question_schema.text == "Test question"
    assert question_schema.subject_id == 1
    assert question_schema.topic_id == 1
    assert question_schema.subtopic_id == 1
    assert question_schema.question_set_ids == [1]
    assert question_schema.difficulty == "Easy"
    assert len(question_schema.answer_choices) == 2
    assert question_schema.explanation == "Test explanation"
