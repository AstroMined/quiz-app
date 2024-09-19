# filename: backend/app/crud/crud_leaderboard.py

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.core.config import TimePeriod
from backend.app.services.logging_service import logger
from backend.app.crud.crud_time_period import read_time_period_from_db, create_time_period_in_db


def create_leaderboard_entry_in_db(db: Session, leaderboard_data: dict) -> LeaderboardModel:
    try:
        logger.debug(f"Attempting to create leaderboard entry with data: {leaderboard_data}")
        
        # Fetch the TimePeriodModel
        time_period_id = leaderboard_data.pop('time_period_id', None)
        if time_period_id is None:
            raise ValueError("time_period_id is required")
        
        time_period = read_time_period_from_db(db, time_period_id)
        if not time_period:
            raise ValueError(f"TimePeriod with id {time_period_id} not found")
        
        # Create the LeaderboardModel with the time_period relationship
        db_leaderboard_entry = LeaderboardModel(**leaderboard_data, time_period=time_period)
        db.add(db_leaderboard_entry)
        db.commit()
        db.refresh(db_leaderboard_entry)
        logger.debug(f"Successfully created leaderboard entry: {db_leaderboard_entry}")
        return db_leaderboard_entry
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemy error creating leaderboard entry: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating leaderboard entry: {str(e)}")
        raise

def read_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> Optional[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_id).first()

def read_leaderboard_entries_from_db(
    db: Session,
    time_period_id: int,
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: int = 100
) -> List[LeaderboardModel]:
    query = db.query(LeaderboardModel).filter(LeaderboardModel.time_period_id == time_period_id)
    if group_id:
        query = query.filter(LeaderboardModel.group_id == group_id)
    if user_id:
        query = query.filter(LeaderboardModel.user_id == user_id)
    return query.order_by(LeaderboardModel.score.desc()).limit(limit).all()

def read_leaderboard_entries_for_user_from_db(db: Session, user_id: int) -> List[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.user_id == user_id).all()

def read_leaderboard_entries_for_group_from_db(db: Session, group_id: int) -> List[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.group_id == group_id).all()

def update_leaderboard_entry_in_db(db: Session, entry_id: int, update_data: dict) -> Optional[LeaderboardModel]:
    try:
        db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == entry_id).first()
        if db_entry:
            for key, value in update_data.items():
                setattr(db_entry, key, value)
            db.commit()
            db.refresh(db_entry)
        return db_entry
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating leaderboard entry: {str(e)}")
        raise

def delete_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> bool:
    try:
        db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_id).first()
        if db_entry:
            db.delete(db_entry)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting leaderboard entry: {str(e)}")
        raise

def read_or_create_time_period_in_db(db: Session, time_period_id: int) -> TimePeriodModel:
    try:
        time_period = TimePeriod(time_period_id)
    except ValueError:
        logger.error(f"Invalid time period id: {time_period_id}")
        raise ValueError(f"Invalid time period id: {time_period_id}")

    return read_time_period_from_db(db, time_period_id) or create_time_period_in_db(db, time_period)
