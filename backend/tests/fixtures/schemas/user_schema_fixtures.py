# filename: backend/tests/fixtures/schemas/user_schema_fixtures.py

import pytest
from datetime import datetime, timezone

from backend.app.schemas.user import UserCreateSchema
from backend.app.schemas.groups import GroupCreateSchema
from backend.app.schemas.roles import RoleCreateSchema
from backend.app.schemas.permissions import PermissionCreateSchema
from backend.app.schemas.leaderboard import LeaderboardCreateSchema
from backend.app.schemas.user_responses import UserResponseCreateSchema


@pytest.fixture(scope="function")
def test_schema_user(test_model_role):
    """Create a test user creation schema."""
    return UserCreateSchema(
        username="testuser",
        email="testuser@example.com",
        password="TestPassword123!",
        role_id=test_model_role.id,
    )


@pytest.fixture(scope="function")
def test_schema_group(test_model_user):
    """Create a test group creation schema."""
    return GroupCreateSchema(
        name="test_schema Group",
        description="This is a test group",
        creator_id=test_model_user.id,
    )


@pytest.fixture(scope="function")
def test_schema_role(test_model_permissions):
    """Create a test role creation schema."""
    role_data = {
        "name": "test_schema Role",
        "description": "This is a test role",
        "permissions": [permission.name for permission in test_model_permissions],
    }
    return RoleCreateSchema(**role_data)


@pytest.fixture(scope="function")
def test_schema_permission():
    """Create a test permission creation schema."""
    return PermissionCreateSchema(
        name="test_schema_permission", description="This is a test permission"
    )


@pytest.fixture(scope="function")
def test_schema_leaderboard(test_model_user):
    """Create a test leaderboard entry schema."""
    return LeaderboardCreateSchema(
        user_id=test_model_user.id, score=100, time_period_id=1
    )


@pytest.fixture(scope="function")
def test_schema_user_response(
    test_model_user, test_model_questions, test_model_answer_choices
):
    """Create a test user response schema."""
    return UserResponseCreateSchema(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
        response_time=10,
        timestamp=datetime.now(timezone.utc),
    )