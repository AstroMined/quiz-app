# filename: backend/tests/unit/models/test_revoked_token_model.py

import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from backend.app.models.authentication import RevokedTokenModel


def test_revoked_token_model_default_revoked_at():
    """Test RevokedTokenModel default revoked_at value logic."""
    # Test that the default lambda function works correctly
    with patch('backend.app.models.authentication.datetime') as mock_datetime:
        test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = test_datetime
        mock_datetime.timezone = timezone
        
        # Get the default function from the Column definition
        revoked_at_default = RevokedTokenModel.__table__.columns['revoked_at'].default.arg
        # SQLAlchemy default functions receive a context parameter
        result = revoked_at_default(None)  # Pass None as context for unit testing
        
        assert result == test_datetime
        mock_datetime.now.assert_called_once_with(timezone.utc)


def test_revoked_token_model_creation_with_explicit_datetime():
    """Test RevokedTokenModel creation with explicit datetime values."""
    test_revoked_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    test_expires_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    
    token = RevokedTokenModel(
        jti="test-jti",
        token="test.token",
        user_id=123,
        revoked_at=test_revoked_at,
        expires_at=test_expires_at
    )
    
    assert token.jti == "test-jti"
    assert token.token == "test.token"
    assert token.user_id == 123
    assert token.revoked_at == test_revoked_at
    assert token.expires_at == test_expires_at


def test_revoked_token_model_creation_minimal():
    """Test RevokedTokenModel creation with minimal required fields."""
    test_expires_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    
    token = RevokedTokenModel(
        jti="test-jti",
        token="test.token",
        user_id=123,
        expires_at=test_expires_at
        # revoked_at will use default
    )
    
    assert token.jti == "test-jti"
    assert token.token == "test.token"
    assert token.user_id == 123
    assert token.expires_at == test_expires_at
    # revoked_at should be set by default lambda, but we can't easily test 
    # the exact value without database interaction


def test_revoked_token_model_repr():
    """Test RevokedTokenModel string representation."""
    test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    token = RevokedTokenModel(
        jti="test-jti-123",
        token="test.token.here",
        user_id=456,
        revoked_at=test_datetime,
        expires_at=test_datetime
    )
    
    expected = "<RevokedTokenModel(jti='test-jti-123', user_id='456', revoked_at='2024-01-01 12:00:00+00:00')>"
    assert repr(token) == expected


def test_revoked_token_model_attributes():
    """Test RevokedTokenModel attribute access."""
    test_revoked_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    test_expires_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    
    token = RevokedTokenModel(
        jti="access-123",
        token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        user_id=789,
        revoked_at=test_revoked_at,
        expires_at=test_expires_at
    )
    
    # Test all attributes are accessible
    assert hasattr(token, 'jti')
    assert hasattr(token, 'token')
    assert hasattr(token, 'user_id')
    assert hasattr(token, 'revoked_at')
    assert hasattr(token, 'expires_at')
    
    # Test attribute values
    assert token.jti == "access-123"
    assert token.token == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    assert token.user_id == 789
    assert token.revoked_at == test_revoked_at
    assert token.expires_at == test_expires_at


def test_revoked_token_model_default_function_uses_utc():
    """Test that the default function specifically uses UTC timezone."""
    # Get the default function from the Column definition
    revoked_at_default = RevokedTokenModel.__table__.columns['revoked_at'].default.arg
    
    # Call the default function with context parameter
    result = revoked_at_default(None)
    
    # Verify it returns a timezone-aware datetime with UTC
    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
    
    # Verify it's close to current time (within 1 second)
    now = datetime.now(timezone.utc)
    time_diff = abs((now - result).total_seconds())
    assert time_diff < 1