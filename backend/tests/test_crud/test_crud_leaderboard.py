# filename: backend/tests/test_crud/test_crud_leaderboard.py

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import TimePeriod
from backend.app.crud.crud_groups import create_group_in_db
from backend.app.crud.crud_leaderboard import (
    create_leaderboard_entry_in_db,
    delete_leaderboard_entry_from_db,
    read_leaderboard_entries_for_group_from_db,
    read_leaderboard_entries_for_user_from_db,
    read_leaderboard_entries_from_db,
    read_leaderboard_entry_from_db,
    read_or_create_time_period_in_db,
    update_leaderboard_entry_in_db,
)
from backend.app.crud.crud_user import create_user_in_db
from backend.app.services.logging_service import logger


def test_create_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(
        db_session, test_schema_leaderboard.model_dump()
    )
    assert entry.user_id == test_schema_leaderboard.user_id
    assert entry.score == test_schema_leaderboard.score
    assert entry.time_period_id == test_schema_leaderboard.time_period_id


def test_read_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(
        db_session, test_schema_leaderboard.model_dump()
    )
    read_entry = read_leaderboard_entry_from_db(db_session, entry.id)
    assert read_entry.id == entry.id
    assert read_entry.user_id == entry.user_id
    assert read_entry.score == entry.score


def test_read_leaderboard_entries(db_session, test_schema_leaderboard):
    create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    entries = read_leaderboard_entries_from_db(
        db_session, test_schema_leaderboard.time_period_id
    )
    assert len(entries) > 0


def test_update_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(
        db_session, test_schema_leaderboard.model_dump()
    )
    updated_data = {"score": 200}
    updated_entry = update_leaderboard_entry_in_db(db_session, entry.id, updated_data)
    assert updated_entry.score == 200


def test_delete_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(
        db_session, test_schema_leaderboard.model_dump()
    )
    assert delete_leaderboard_entry_from_db(db_session, entry.id) is True
    assert read_leaderboard_entry_from_db(db_session, entry.id) is None


def test_read_or_create_time_period(db_session):
    time_period = read_or_create_time_period_in_db(db_session, time_period_id=1)
    assert time_period.id == 1
    assert time_period.name == "daily"


def test_read_leaderboard_entries_for_user(
    db_session, test_schema_leaderboard, test_user_data
):
    user = create_user_in_db(db_session, test_user_data)
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["user_id"] = user.id
    create_leaderboard_entry_in_db(db_session, leaderboard_data)
    entries = read_leaderboard_entries_for_user_from_db(db_session, user.id)
    assert len(entries) == 1
    assert entries[0].user_id == user.id


def test_read_leaderboard_entries_for_group(
    db_session, test_schema_leaderboard, test_schema_group
):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["group_id"] = group.id
    create_leaderboard_entry_in_db(db_session, leaderboard_data)
    entries = read_leaderboard_entries_for_group_from_db(db_session, group.id)
    assert len(entries) == 1
    assert entries[0].group_id == group.id


def test_create_leaderboard_entry_with_invalid_time_period(
    db_session, test_schema_leaderboard
):
    invalid_data = test_schema_leaderboard.model_dump()
    invalid_data["time_period_id"] = 9999  # Invalid time period ID
    with pytest.raises(ValueError):
        create_leaderboard_entry_in_db(db_session, invalid_data)


def test_read_leaderboard_entries_with_filters(
    db_session, test_schema_leaderboard, test_user_data, test_group_data
):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)

    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["user_id"] = user.id
    leaderboard_data["group_id"] = group.id

    time_period_id = leaderboard_data["time_period_id"]

    created_leaderboard_entry = create_leaderboard_entry_in_db(
        db_session, leaderboard_data
    )

    entries = read_leaderboard_entries_from_db(
        db_session, time_period_id=time_period_id, group_id=group.id, user_id=user.id
    )
    assert len(entries) == 1
    assert entries[0].user_id == user.id
    assert entries[0].group_id == group.id


def test_update_nonexistent_leaderboard_entry(db_session):
    non_existent_id = 9999
    updated_data = {"score": 200}
    result = update_leaderboard_entry_in_db(db_session, non_existent_id, updated_data)
    assert result is None


def test_delete_nonexistent_leaderboard_entry(db_session):
    non_existent_id = 9999
    result = delete_leaderboard_entry_from_db(db_session, non_existent_id)
    assert result is False


@pytest.mark.parametrize("time_period_id", [tp.value for tp in TimePeriod])
def test_read_or_create_all_time_periods(db_session, time_period_id):
    time_period = read_or_create_time_period_in_db(db_session, time_period_id)
    assert time_period.id == time_period_id
    assert time_period.name == TimePeriod(time_period_id).name.lower()


def test_read_leaderboard_entries_empty_result(db_session):
    entries = read_leaderboard_entries_from_db(
        db_session, time_period_id=1, group_id=9999, user_id=9999
    )
    assert len(entries) == 0


# Note: The following test assumes that SQLAlchemyError can be triggered by passing invalid data.
# You might need to adjust this based on your actual database constraints.
def test_create_leaderboard_entry_sql_error(db_session, test_schema_leaderboard):
    invalid_data = test_schema_leaderboard.model_dump()
    invalid_data["user_id"] = None  # Assuming user_id is non-nullable
    with pytest.raises(SQLAlchemyError):
        create_leaderboard_entry_in_db(db_session, invalid_data)


def test_create_multiple_leaderboard_entries(
    db_session, test_schema_leaderboard, test_user_data
):
    user = create_user_in_db(db_session, test_user_data)
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["user_id"] = user.id

    # Create entries for different time periods
    for time_period in TimePeriod:
        leaderboard_data["time_period_id"] = time_period.value
        create_leaderboard_entry_in_db(db_session, leaderboard_data)

    entries = read_leaderboard_entries_for_user_from_db(db_session, user.id)
    assert len(entries) == len(TimePeriod)


def test_update_leaderboard_entry_score(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(
        db_session, test_schema_leaderboard.model_dump()
    )
    new_score = entry.score + 100
    updated_entry = update_leaderboard_entry_in_db(
        db_session, entry.id, {"score": new_score}
    )
    assert updated_entry.score == new_score


def test_read_leaderboard_entries_ordering(
    db_session, test_schema_leaderboard, test_user_data
):
    user1 = create_user_in_db(db_session, test_user_data)
    user2 = create_user_in_db(
        db_session,
        {**test_user_data, "username": "testuser2", "email": "testuser2@example.com"},
    )

    leaderboard_data1 = test_schema_leaderboard.model_dump()
    leaderboard_data1["user_id"] = user1.id
    leaderboard_data1["score"] = 100

    leaderboard_data2 = test_schema_leaderboard.model_dump()
    leaderboard_data2["user_id"] = user2.id
    leaderboard_data2["score"] = 200

    create_leaderboard_entry_in_db(db_session, leaderboard_data1)
    create_leaderboard_entry_in_db(db_session, leaderboard_data2)

    entries = read_leaderboard_entries_from_db(
        db_session, time_period_id=test_schema_leaderboard.time_period_id
    )
    assert len(entries) == 2
    assert entries[0].score > entries[1].score


def test_read_leaderboard_entries_with_limit(
    db_session, test_schema_leaderboard, test_user_data
):
    user = create_user_in_db(db_session, test_user_data)
    leaderboard_data = test_schema_leaderboard.model_dump()
    logger.debug("test_user_data: %s", test_user_data)
    leaderboard_data["user_id"] = user.id
    logger.debug("leaderboard_data: %s", leaderboard_data)

    for i in range(5):
        leaderboard_data["score"] = i * 100
        leaderboard_data["time_period_id"] = test_schema_leaderboard.time_period_id
        logger.debug("leaderboard_data for i=%s: %s", i, leaderboard_data)
        create_leaderboard_entry_in_db(db_session, leaderboard_data)

    entries_without_limit = read_leaderboard_entries_from_db(
        db_session, time_period_id=test_schema_leaderboard.time_period_id
    )
    assert len(entries_without_limit) == 5

    entries_with_limit = read_leaderboard_entries_from_db(
        db_session, time_period_id=test_schema_leaderboard.time_period_id, limit=3
    )
    assert len(entries_with_limit) == 3


def test_read_leaderboard_entries_for_nonexistent_group(db_session):
    entries = read_leaderboard_entries_for_group_from_db(db_session, group_id=9999)
    assert len(entries) == 0


def test_read_leaderboard_entries_for_nonexistent_user(db_session):
    entries = read_leaderboard_entries_for_user_from_db(db_session, user_id=9999)
    assert len(entries) == 0
