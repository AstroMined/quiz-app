# filename: backend/tests/test_services/test_scoring_service.py

import pytest
from datetime import datetime, timedelta, timezone
from backend.app.services.scoring_service import (
    calculate_user_score,
    calculate_leaderboard_scores,
    time_period_to_schema,
    leaderboard_to_schema
)
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.time_period import TimePeriodModel
from backend.app.schemas.leaderboard import LeaderboardSchema, TimePeriodSchema
from backend.app.core.config import TimePeriod

def test_calculate_user_score(db_session):
    # Create a test user
    user = UserModel(username="testuser", email="testuser@example.com")
    db_session.add(user)
    db_session.commit()

    # Create some test responses
    responses = [
        UserResponseModel(user_id=user.id, is_correct=True),
        UserResponseModel(user_id=user.id, is_correct=False),
        UserResponseModel(user_id=user.id, is_correct=True)
    ]
    db_session.add_all(responses)
    db_session.commit()

    # Calculate the score
    score = calculate_user_score(user.id, db_session)
    assert score == 2

def test_calculate_leaderboard_scores(db_session):
    # Create test users and groups
    user1 = UserModel(username="user1", email="user1@example.com")
    user2 = UserModel(username="user2", email="user2@example.com")
    db_session.add_all([user1, user2])
    db_session.commit()

    group = UserToGroupAssociation(user_id=user1.id, group_id=1)
    db_session.add(group)
    db_session.commit()

    # Create test responses
    now = datetime.now(timezone.utc)
    responses = [
        UserResponseModel(user_id=user1.id, is_correct=True, timestamp=now - timedelta(hours=1)),
        UserResponseModel(user_id=user1.id, is_correct=True, timestamp=now - timedelta(days=2)),
        UserResponseModel(user_id=user2.id, is_correct=True, timestamp=now - timedelta(hours=2)),
    ]
    db_session.add_all(responses)
    db_session.commit()

    # Test daily leaderboard
    daily_scores = calculate_leaderboard_scores(db_session, TimePeriodModel(id=TimePeriod.DAILY.value))
    assert daily_scores == {user1.id: 1, user2.id: 1}

    # Test weekly leaderboard
    weekly_scores = calculate_leaderboard_scores(db_session, TimePeriodModel(id=TimePeriod.WEEKLY.value))
    assert weekly_scores == {user1.id: 2, user2.id: 1}

    # Test group leaderboard
    group_scores = calculate_leaderboard_scores(db_session, TimePeriodModel(id=TimePeriod.WEEKLY.value), group_id=1)
    assert group_scores == {user1.id: 2}

def test_time_period_to_schema():
    time_period_model = TimePeriodModel(id=1, name="Daily")
    schema = time_period_to_schema(time_period_model)
    assert isinstance(schema, TimePeriodSchema)
    assert schema.id == 1
    assert schema.name == "Daily"

def test_leaderboard_to_schema():
    time_period_model = TimePeriodModel(id=1, name="Daily")
    leaderboard_model = type('LeaderboardModel', (), {
        'id': 1,
        'user_id': 2,
        'score': 10,
        'time_period': time_period_model,
        'group_id': 3
    })()
    schema = leaderboard_to_schema(leaderboard_model)
    assert isinstance(schema, LeaderboardSchema)
    assert schema.id == 1
    assert schema.user_id == 2
    assert schema.score == 10
    assert schema.time_period.id == 1
    assert schema.time_period.name == "Daily"
    assert schema.group_id == 3
