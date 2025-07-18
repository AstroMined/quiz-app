# filename: backend/tests/test_schemas_leaderboard.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.leaderboard import (
    LeaderboardBaseSchema,
    LeaderboardCreateSchema,
    LeaderboardSchema,
    LeaderboardUpdateSchema,
    TimePeriodSchema,
)


def test_leaderboard_base_schema_valid():
    data = {"user_id": 1, "score": 100}
    schema = LeaderboardBaseSchema(**data)
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.group_id is None


def test_leaderboard_base_schema_with_group():
    data = {"user_id": 1, "score": 100, "group_id": 5}
    schema = LeaderboardBaseSchema(**data)
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.group_id == 5


def test_leaderboard_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        LeaderboardBaseSchema(user_id=0, score=100, time_period_id=1)
    assert "Input should be greater than 0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        LeaderboardBaseSchema(user_id=1, score=-1, time_period_id=1)
    assert "Input should be greater than or equal to 0" in str(exc_info.value)


def test_leaderboard_create_schema():
    data = {"user_id": 1, "score": 100, "time_period_id": 1, "group_id": 5}
    schema = LeaderboardCreateSchema(**data)
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.time_period_id == 1
    assert schema.group_id == 5


def test_leaderboard_update_schema():
    data = {"score": 150}
    schema = LeaderboardUpdateSchema(**data)
    assert schema.score == 150


def test_leaderboard_schema():
    time_period = TimePeriodSchema(id=1, name="daily")
    data = {
        "id": 1,
        "user_id": 1,
        "score": 100,
        "time_period": time_period,
        "time_period_id": time_period.id,
        "group_id": 5,
    }
    schema = LeaderboardSchema(**data)
    assert schema.id == 1
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.time_period == time_period
    assert schema.group_id == 5



def test_time_period_schema():
    data = {"id": 1, "name": "daily"}
    schema = TimePeriodSchema(**data)
    assert schema.id == 1
    assert schema.name == "daily"
