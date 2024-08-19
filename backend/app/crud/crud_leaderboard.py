# filename: backend/app/crud/crud_leaderboard.py

from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.time_period import TimePeriodModel


def create_leaderboard_entry_in_db(db: Session, leaderboard_data: dict) -> LeaderboardModel:
    db_leaderboard_entry = LeaderboardModel(**leaderboard_data)
    db.add(db_leaderboard_entry)
    db.commit()
    db.refresh(db_leaderboard_entry)
    return db_leaderboard_entry

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
    db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == entry_id).first()
    if db_entry:
        for key, value in update_data.items():
            setattr(db_entry, key, value)
        db.commit()
        db.refresh(db_entry)
    return db_entry

def delete_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> bool:
    db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_id).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        return True
    return False

def read_or_create_time_period_in_db(db: Session, time_period_data: dict) -> TimePeriodModel:
    db_time_period = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_data['id']).first()
    if not db_time_period:
        db_time_period = TimePeriodModel(**time_period_data)
        db.add(db_time_period)
        db.commit()
        db.refresh(db_time_period)
    return db_time_period
