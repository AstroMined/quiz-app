# filename: backend/app/crud/crud_leaderboard.py

"""
This module handles CRUD operations for leaderboard entries in the database.

It provides functions for creating, reading, updating, and deleting leaderboard entries,
as well as managing time periods associated with leaderboard entries.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.core.config: For TimePeriod enum
- backend.app.crud.crud_time_period: For time period related operations
- backend.app.models.leaderboard: For the LeaderboardModel
- backend.app.models.time_period: For the TimePeriodModel
- backend.app.services.logging_service: For logging

Main functions:
- create_leaderboard_entry_in_db: Creates a new leaderboard entry
- read_leaderboard_entry_from_db: Retrieves a single leaderboard entry by ID
- read_leaderboard_entries_from_db: Retrieves multiple leaderboard entries with filters
- read_leaderboard_entries_for_user_from_db: Retrieves leaderboard entries for a specific user
- read_leaderboard_entries_for_group_from_db: Retrieves leaderboard entries for a specific group
- update_leaderboard_entry_in_db: Updates an existing leaderboard entry
- delete_leaderboard_entry_from_db: Deletes a leaderboard entry
- read_or_create_time_period_in_db: Retrieves or creates a time period

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_leaderboard import create_leaderboard_entry_in_db

    def add_new_leaderboard_entry(db: Session, user_id: int, score: int, time_period_id: int):
        leaderboard_data = {"user_id": user_id, "score": score, "time_period_id": time_period_id}
        return create_leaderboard_entry_in_db(db, leaderboard_data)
"""

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import TimePeriod
from backend.app.crud.crud_time_period import (
    create_time_period_in_db,
    read_time_period_from_db,
)
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.services.logging_service import logger


def create_leaderboard_entry_in_db(
    db: Session, leaderboard_data: dict
) -> LeaderboardModel:
    """
    Create a new leaderboard entry in the database.

    Args:
        db (Session): The database session.
        leaderboard_data (dict): A dictionary containing the leaderboard entry data.
            Required keys: "time_period_id"
            Other keys should match the LeaderboardModel fields.

    Returns:
        LeaderboardModel: The created leaderboard entry database object.

    Raises:
        ValueError: If time_period_id is not provided or the TimePeriod is not found.
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        leaderboard_data = {
            "user_id": 1,
            "score": 100,
            "time_period_id": 1
        }
        new_entry = create_leaderboard_entry_in_db(db, leaderboard_data)
    """
    try:
        logger.debug(
            "Attempting to create leaderboard entry with data: %s", leaderboard_data
        )

        # Fetch the TimePeriodModel
        time_period_id = leaderboard_data.pop("time_period_id", None)
        if time_period_id is None:
            raise ValueError("time_period_id is required")

        time_period = read_time_period_from_db(db, time_period_id)
        if not time_period:
            raise ValueError(f"TimePeriod with id {time_period_id} not found")

        # Create the LeaderboardModel with the time_period relationship
        db_leaderboard_entry = LeaderboardModel(
            **leaderboard_data, time_period=time_period
        )
        db.add(db_leaderboard_entry)
        db.commit()
        db.refresh(db_leaderboard_entry)
        logger.debug("Successfully created leaderboard entry: %s", db_leaderboard_entry)
        return db_leaderboard_entry
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("SQLAlchemy error creating leaderboard entry: %s", str(e))
        raise
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error creating leaderboard entry: %s", str(e))
        raise


def read_leaderboard_entry_from_db(
    db: Session, leaderboard_id: int
) -> Optional[LeaderboardModel]:
    """
    Retrieve a single leaderboard entry from the database by its ID.

    Args:
        db (Session): The database session.
        leaderboard_id (int): The ID of the leaderboard entry to retrieve.

    Returns:
        Optional[LeaderboardModel]: The retrieved leaderboard entry database object,
        or None if not found.

    Usage example:
        entry = read_leaderboard_entry_from_db(db, 1)
        if entry:
            print(f"User {entry.user_id} score: {entry.score}")
    """
    return (
        db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_id).first()
    )


def read_leaderboard_entries_from_db(
    db: Session,
    time_period_id: int,
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
) -> List[LeaderboardModel]:
    """
    Retrieve multiple leaderboard entries from the database with filters.

    Args:
        db (Session): The database session.
        time_period_id (int): The ID of the time period to filter by.
        group_id (Optional[int], optional): The ID of the group to filter by. Defaults to None.
        user_id (Optional[int], optional): The ID of the user to filter by. Defaults to None.
        limit (int, optional): The maximum number of entries to return. Defaults to 100.

    Returns:
        List[LeaderboardModel]: A list of retrieved leaderboard entry database objects.

    Usage example:
        entries = read_leaderboard_entries_from_db(db, time_period_id=1, group_id=2, limit=10)
        for entry in entries:
            print(f"User {entry.user_id} score: {entry.score}")
    """
    query = db.query(LeaderboardModel).filter(
        LeaderboardModel.time_period_id == time_period_id
    )
    if group_id:
        query = query.filter(LeaderboardModel.group_id == group_id)
    if user_id:
        query = query.filter(LeaderboardModel.user_id == user_id)
    return query.order_by(LeaderboardModel.score.desc()).limit(limit).all()


def read_leaderboard_entries_for_user_from_db(
    db: Session, user_id: int
) -> List[LeaderboardModel]:
    """
    Retrieve all leaderboard entries for a specific user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to retrieve entries for.

    Returns:
        List[LeaderboardModel]: A list of leaderboard entry database objects for the user.

    Usage example:
        user_entries = read_leaderboard_entries_for_user_from_db(db, user_id=1)
        for entry in user_entries:
            print(f"Time period: {entry.time_period_id}, Score: {entry.score}")
    """
    return db.query(LeaderboardModel).filter(LeaderboardModel.user_id == user_id).all()


def read_leaderboard_entries_for_group_from_db(
    db: Session, group_id: int
) -> List[LeaderboardModel]:
    """
    Retrieve all leaderboard entries for a specific group from the database.

    Args:
        db (Session): The database session.
        group_id (int): The ID of the group to retrieve entries for.

    Returns:
        List[LeaderboardModel]: A list of leaderboard entry database objects for the group.

    Usage example:
        group_entries = read_leaderboard_entries_for_group_from_db(db, group_id=1)
        for entry in group_entries:
            print(f"User: {entry.user_id}, Score: {entry.score}")
    """
    return (
        db.query(LeaderboardModel).filter(LeaderboardModel.group_id == group_id).all()
    )


def update_leaderboard_entry_in_db(
    db: Session, entry_id: int, update_data: dict
) -> Optional[LeaderboardModel]:
    """
    Update an existing leaderboard entry in the database.

    Args:
        db (Session): The database session.
        entry_id (int): The ID of the leaderboard entry to update.
        update_data (dict): A dictionary containing the updated leaderboard entry data.

    Returns:
        Optional[LeaderboardModel]: The updated leaderboard entry database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"score": 150}
        updated_entry = update_leaderboard_entry_in_db(db, entry_id=1, update_data=updated_data)
        if updated_entry:
            print(f"Updated score: {updated_entry.score}")
    """
    try:
        db_entry = (
            db.query(LeaderboardModel).filter(LeaderboardModel.id == entry_id).first()
        )
        if db_entry:
            for key, value in update_data.items():
                setattr(db_entry, key, value)
            db.commit()
            db.refresh(db_entry)
        return db_entry
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error updating leaderboard entry: %s", str(e))
        raise


def delete_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> bool:
    """
    Delete a leaderboard entry from the database.

    Args:
        db (Session): The database session.
        leaderboard_id (int): The ID of the leaderboard entry to delete.

    Returns:
        bool: True if the leaderboard entry was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_leaderboard_entry_from_db(db, leaderboard_id=1):
            print("Leaderboard entry successfully deleted")
        else:
            print("Leaderboard entry not found or couldn't be deleted")
    """
    try:
        db_entry = (
            db.query(LeaderboardModel)
            .filter(LeaderboardModel.id == leaderboard_id)
            .first()
        )
        if db_entry:
            db.delete(db_entry)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error deleting leaderboard entry: %s", str(e))
        raise


def read_or_create_time_period_in_db(
    db: Session, time_period_id: int
) -> TimePeriodModel:
    """
    Retrieve or create a time period in the database.

    This function first attempts to read an existing time period. If it doesn't exist,
    it creates a new one.

    Args:
        db (Session): The database session.
        time_period_id (int): The ID of the time period to retrieve or create.

    Returns:
        TimePeriodModel: The retrieved or created time period database object.

    Raises:
        ValueError: If the provided time_period_id is invalid.

    Usage example:
        time_period = read_or_create_time_period_in_db(db, time_period_id=1)
        print(f"Time period: {time_period.name}")
    """
    try:
        time_period = TimePeriod(time_period_id)
    except ValueError as exc:
        logger.error("Invalid time period id: %s", time_period_id)
        raise ValueError(f"Invalid time period id: {time_period_id}") from exc

    return read_time_period_from_db(db, time_period_id) or create_time_period_in_db(
        db, time_period
    )
