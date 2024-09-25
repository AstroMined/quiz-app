# filename: backend/app/crud/crud_time_period.py

"""
This module handles CRUD operations for time periods in the database.

It provides functions for creating, reading, updating, and deleting time periods,
as well as initializing the database with predefined time periods.

Key dependencies:
- sqlalchemy.orm: For database session management
- sqlalchemy.exc: For handling SQLAlchemyError
- backend.app.core.config: For TimePeriod enum
- backend.app.models.time_period: For the TimePeriodModel
- backend.app.services.logging_service: For logging

Main functions:
- create_time_period_in_db: Creates a new time period
- read_time_period_from_db: Retrieves a single time period by ID
- read_all_time_periods_from_db: Retrieves all time periods
- update_time_period_in_db: Updates an existing time period
- delete_time_period_from_db: Deletes a time period
- init_time_periods_in_db: Initializes the database with predefined time periods

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_time_period import init_time_periods_in_db

    def initialize_time_periods(db: Session):
        init_time_periods_in_db(db)
"""

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import TimePeriod
from backend.app.models.time_period import TimePeriodModel
from backend.app.services.logging_service import logger


def create_time_period_in_db(db: Session, time_period: TimePeriod) -> TimePeriodModel:
    """
    Create a new time period in the database.

    Args:
        db (Session): The database session.
        time_period (TimePeriod): The TimePeriod enum value to create.

    Returns:
        TimePeriodModel: The created time period database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        new_time_period = create_time_period_in_db(db, TimePeriod.DAILY)
    """
    try:
        db_time_period = TimePeriodModel(
            id=time_period.value, name=time_period.name.lower()
        )
        db.add(db_time_period)
        db.commit()
        db.refresh(db_time_period)
        return db_time_period
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error creating time period: %s", str(e))
        raise


def read_time_period_from_db(
    db: Session, time_period_id: int
) -> Optional[TimePeriodModel]:
    """
    Retrieve a single time period from the database by its ID.

    Args:
        db (Session): The database session.
        time_period_id (int): The ID of the time period to retrieve.

    Returns:
        Optional[TimePeriodModel]: The retrieved time period database object,
        or None if not found.

    Usage example:
        time_period = read_time_period_from_db(db, 1)
        if time_period:
            print(f"Time period name: {time_period.name}")
    """
    return (
        db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_id).first()
    )


def read_all_time_periods_from_db(db: Session) -> List[TimePeriodModel]:
    """
    Retrieve all time periods from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[TimePeriodModel]: A list of all time period database objects.

    Usage example:
        time_periods = read_all_time_periods_from_db(db)
        for period in time_periods:
            print(f"Time period: {period.name}")
    """
    return db.query(TimePeriodModel).all()


def update_time_period_in_db(
    db: Session, time_period_id: int, new_name: str
) -> Optional[TimePeriodModel]:
    """
    Update an existing time period in the database.

    Args:
        db (Session): The database session.
        time_period_id (int): The ID of the time period to update.
        new_name (str): The new name for the time period.

    Returns:
        Optional[TimePeriodModel]: The updated time period database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_period = update_time_period_in_db(db, 1, "new_daily")
        if updated_period:
            print(f"Updated time period name: {updated_period.name}")
    """
    try:
        db_time_period = (
            db.query(TimePeriodModel)
            .filter(TimePeriodModel.id == time_period_id)
            .first()
        )
        if db_time_period:
            db_time_period.name = new_name
            db.commit()
            db.refresh(db_time_period)
        return db_time_period
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error updating time period: %s", str(e))
        raise


def delete_time_period_from_db(db: Session, time_period_id: int) -> bool:
    """
    Delete a time period from the database.

    Args:
        db (Session): The database session.
        time_period_id (int): The ID of the time period to delete.

    Returns:
        bool: True if the time period was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_time_period_from_db(db, 1):
            print("Time period successfully deleted")
        else:
            print("Time period not found or couldn't be deleted")
    """
    try:
        db_time_period = (
            db.query(TimePeriodModel)
            .filter(TimePeriodModel.id == time_period_id)
            .first()
        )
        if db_time_period:
            db.delete(db_time_period)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error deleting time period: %s", str(e))
        raise


def init_time_periods_in_db(db: Session) -> None:
    """
    Initialize the database with predefined time periods.

    This function checks for existing time periods and adds any missing ones
    from the TimePeriod enum.

    Args:
        db (Session): The database session.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        init_time_periods_in_db(db)
    """
    try:
        existing_periods = read_all_time_periods_from_db(db)
        existing_ids = {period.id for period in existing_periods}

        for time_period in TimePeriod:
            if time_period.value not in existing_ids:
                create_time_period_in_db(db, time_period)

        logger.info("Time periods initialized successfully")
    except SQLAlchemyError as e:
        logger.exception("Error initializing time periods: %s", str(e))
        raise
