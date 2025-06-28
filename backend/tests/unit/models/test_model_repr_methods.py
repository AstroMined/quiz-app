# filename: backend/tests/unit/models/test_model_repr_methods.py

import pytest
from datetime import datetime, timezone

from backend.app.core.config import DifficultyLevel
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.questions import QuestionModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.models.users import UserModel


def test_user_model_repr():
    """Test UserModel string representation."""
    user = UserModel(
        id=1,
        username="testuser",
        email="test@example.com",
        role_id=2,
        hashed_password="hashedpass"
    )
    expected = "<User(id=1, username='testuser', email='test@example.com', role_id='2')>"
    assert repr(user) == expected


def test_user_model_repr_with_different_values():
    """Test UserModel repr with different field values."""
    user = UserModel(
        id=999,
        username="admin_user",
        email="admin@company.com",
        role_id=1,
        hashed_password="secure_hash"
    )
    expected = "<User(id=999, username='admin_user', email='admin@company.com', role_id='1')>"
    assert repr(user) == expected


def test_question_model_repr():
    """Test QuestionModel string representation."""
    question = QuestionModel(
        id=1,
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    expected = "<QuestionModel(id=1, text='What is the capital of France?...', difficulty='DifficultyLevel.EASY')>"
    assert repr(question) == expected


def test_question_model_repr_with_long_text():
    """Test QuestionModel repr with text truncation."""
    long_text = "This is a very long question text that should be truncated in the repr method to show only the first 50 characters"
    question = QuestionModel(
        id=2,
        text=long_text,
        difficulty=DifficultyLevel.HARD
    )
    expected = f"<QuestionModel(id=2, text='{long_text[:50]}...', difficulty='DifficultyLevel.HARD')>"
    assert repr(question) == expected


def test_question_model_repr_with_short_text():
    """Test QuestionModel repr with text shorter than 50 chars."""
    short_text = "Short question?"
    question = QuestionModel(
        id=3,
        text=short_text,
        difficulty=DifficultyLevel.MEDIUM
    )
    expected = f"<QuestionModel(id=3, text='{short_text[:50]}...', difficulty='DifficultyLevel.MEDIUM')>"
    assert repr(question) == expected


def test_answer_choice_model_repr():
    """Test AnswerChoiceModel string representation."""
    answer = AnswerChoiceModel(
        id=1,
        text="Paris",
        is_correct=True
    )
    expected = "<AnswerChoiceModel(id=1, text='Paris...', is_correct=True)>"
    assert repr(answer) == expected


def test_answer_choice_model_repr_with_long_text():
    """Test AnswerChoiceModel repr with text truncation."""
    long_text = "This is a very long answer choice text that should be truncated in the repr method"
    answer = AnswerChoiceModel(
        id=2,
        text=long_text,
        is_correct=False
    )
    expected = f"<AnswerChoiceModel(id=2, text='{long_text[:50]}...', is_correct=False)>"
    assert repr(answer) == expected


def test_answer_choice_model_repr_incorrect_answer():
    """Test AnswerChoiceModel repr with incorrect answer."""
    answer = AnswerChoiceModel(
        id=3,
        text="London",
        is_correct=False
    )
    expected = "<AnswerChoiceModel(id=3, text='London...', is_correct=False)>"
    assert repr(answer) == expected


def test_revoked_token_model_repr():
    """Test RevokedTokenModel string representation."""
    test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    token = RevokedTokenModel(
        jti="test-jti-123",
        user_id=456,
        revoked_at=test_datetime,
        token="test.token.here",
        expires_at=test_datetime
    )
    expected = "<RevokedTokenModel(jti='test-jti-123', user_id='456', revoked_at='2024-01-01 12:00:00+00:00')>"
    assert repr(token) == expected


def test_revoked_token_model_repr_with_different_values():
    """Test RevokedTokenModel repr with different values."""
    test_datetime = datetime(2023, 12, 25, 15, 30, 45, tzinfo=timezone.utc)
    token = RevokedTokenModel(
        jti="another-jti-456",
        user_id=789,
        revoked_at=test_datetime,
        token="different.token.value",
        expires_at=test_datetime
    )
    expected = "<RevokedTokenModel(jti='another-jti-456', user_id='789', revoked_at='2023-12-25 15:30:45+00:00')>"
    assert repr(token) == expected


def test_time_period_model_repr():
    """Test TimePeriodModel string representation."""
    # This was already tested in test_time_period_model.py but included for completeness
    model = TimePeriodModel(id=7, name="weekly")
    expected = "<TimePeriodModel(id=7, name='weekly')"
    assert repr(model) == expected


def test_repr_methods_handle_none_values():
    """Test repr methods handle None values gracefully."""
    # Test with minimal required fields
    user = UserModel(
        username="testuser",
        email="test@example.com", 
        hashed_password="hash"
        # id and role_id will be None
    )
    repr_result = repr(user)
    assert "testuser" in repr_result
    assert "test@example.com" in repr_result
    
    question = QuestionModel(
        text="Test question",
        difficulty=DifficultyLevel.EASY
        # id will be None
    )
    repr_result = repr(question)
    assert "Test question" in repr_result
    assert "DifficultyLevel.EASY" in repr_result