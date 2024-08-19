# filename: backend/tests/crud/test_crud_leaderboard.py

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.crud.crud_groups import create_group_in_db
from backend.app.crud.crud_leaderboard import (
    create_leaderboard_entry_in_db, delete_leaderboard_entry_from_db,
    read_leaderboard_entries_for_group_from_db,
    read_leaderboard_entries_for_user_from_db,
    read_leaderboard_entries_from_db, read_leaderboard_entry_from_db,
    read_or_create_time_period_in_db, update_leaderboard_entry_in_db)
from backend.app.crud.crud_user import create_user_in_db


def test_create_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    assert entry.user_id == test_schema_leaderboard.user_id
    assert entry.score == test_schema_leaderboard.score
    assert entry.time_period_id == test_schema_leaderboard.time_period_id

def test_read_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    read_entry = read_leaderboard_entry_from_db(db_session, entry.id)
    assert read_entry.id == entry.id
    assert read_entry.user_id == entry.user_id
    assert read_entry.score == entry.score

def test_read_leaderboard_entries(db_session, test_schema_leaderboard):
    create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    entries = read_leaderboard_entries_from_db(db_session, test_schema_leaderboard.time_period_id)
    assert len(entries) > 0

def test_update_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    updated_data = {"score": 200}
    updated_entry = update_leaderboard_entry_in_db(db_session, entry.id, updated_data)
    assert updated_entry.score == 200

def test_delete_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    assert delete_leaderboard_entry_from_db(db_session, entry.id) is True
    assert read_leaderboard_entry_from_db(db_session, entry.id) is None

def test_read_or_create_time_period(db_session):
    time_period_data = {"id": 1, "name": "daily"}
    time_period = read_or_create_time_period_in_db(db_session, time_period_data)
    assert time_period.id == 1
    assert time_period.name == "daily"

def test_read_leaderboard_entries_for_user(db_session, test_schema_leaderboard, test_schema_user):
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["user_id"] = user.id
    create_leaderboard_entry_in_db(db_session, leaderboard_data)
    entries = read_leaderboard_entries_for_user_from_db(db_session, user.id)
    assert len(entries) == 1
    assert entries[0].user_id == user.id

def test_read_leaderboard_entries_for_group(db_session, test_schema_leaderboard, test_schema_group):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["group_id"] = group.id
    create_leaderboard_entry_in_db(db_session, leaderboard_data)
    entries = read_leaderboard_entries_for_group_from_db(db_session, group.id)
    assert len(entries) == 1
    assert entries[0].group_id == group.id
