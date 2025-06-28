# filename: backend/tests/unit/models/test_model_defaults.py

import pytest

from backend.app.models.users import UserModel


def test_user_model_default_is_active():
    """Test UserModel default value for is_active when not explicitly set."""
    # SQLAlchemy defaults work at the database level, not at the Python object level
    # So we test the Column default value directly
    column_default = UserModel.__table__.columns['is_active'].default
    assert column_default.arg is True


def test_user_model_default_is_admin():
    """Test UserModel default value for is_admin when not explicitly set."""
    # SQLAlchemy defaults work at the database level, not at the Python object level
    # So we test the Column default value directly
    column_default = UserModel.__table__.columns['is_admin'].default
    assert column_default.arg is False


def test_user_model_explicit_is_active_true():
    """Test UserModel with explicitly set is_active=True."""
    user = UserModel(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role_id=1,
        is_active=True
    )
    
    assert user.is_active is True


def test_user_model_explicit_is_active_false():
    """Test UserModel with explicitly set is_active=False."""
    user = UserModel(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role_id=1,
        is_active=False
    )
    
    assert user.is_active is False


def test_user_model_explicit_is_admin_true():
    """Test UserModel with explicitly set is_admin=True."""
    user = UserModel(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role_id=1,
        is_admin=True
    )
    
    assert user.is_admin is True


def test_user_model_explicit_is_admin_false():
    """Test UserModel with explicitly set is_admin=False."""
    user = UserModel(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role_id=1,
        is_admin=False
    )
    
    assert user.is_admin is False


def test_user_model_admin_user_creation():
    """Test creating an admin user with both flags."""
    admin_user = UserModel(
        username="admin",
        email="admin@example.com",
        hashed_password="secure_hash",
        role_id=1,
        is_active=True,
        is_admin=True
    )
    
    assert admin_user.is_active is True
    assert admin_user.is_admin is True
    assert admin_user.username == "admin"
    assert admin_user.email == "admin@example.com"


def test_user_model_inactive_user_creation():
    """Test creating an inactive user."""
    inactive_user = UserModel(
        username="inactive",
        email="inactive@example.com",
        hashed_password="hash",
        role_id=2,
        is_active=False,
        is_admin=False
    )
    
    assert inactive_user.is_active is False
    assert inactive_user.is_admin is False


def test_user_model_all_required_fields():
    """Test UserModel with all required fields."""
    user = UserModel(
        username="complete_user",
        email="complete@example.com",
        hashed_password="secure_password_hash",
        role_id=3
    )
    
    # Required fields
    assert user.username == "complete_user"
    assert user.email == "complete@example.com"
    assert user.hashed_password == "secure_password_hash"
    assert user.role_id == 3
    
    # Optional fields (should be None when not set without database)
    assert user.id is None  # Will be set by database
    assert user.token_blacklist_date is None  # Has server_default in DB
    # is_active and is_admin defaults only apply at database level


def test_user_model_boolean_field_types():
    """Test that boolean fields accept boolean values."""
    # Test with explicit values
    user_explicit = UserModel(
        username="test2",
        email="test2@example.com",
        hashed_password="hash",
        role_id=1,
        is_active=False,
        is_admin=True
    )
    
    assert isinstance(user_explicit.is_active, bool)
    assert isinstance(user_explicit.is_admin, bool)
    assert user_explicit.is_active is False
    assert user_explicit.is_admin is True