# filename: app/crud/crud_leaderboard.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.leaderboard import LeaderboardModel
from app.models.time_period import TimePeriodModel

def create_leaderboard_entry_in_db(db: Session, leaderboard_data: Dict) -> LeaderboardModel:
    db_leaderboard_entry = LeaderboardModel(
        user_id=leaderboard_data['user_id'],
        score=leaderboard_data['score'],
        time_period_id=leaderboard_data['time_period_id'],
        group_id=leaderboard_data.get('group_id')
    )
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
    skip: int = 0,
    limit: int = 100
) -> List[LeaderboardModel]:
    query = db.query(LeaderboardModel).filter(LeaderboardModel.time_period_id == time_period_id)
    if group_id:
        query = query.filter(LeaderboardModel.group_id == group_id)
    return query.order_by(LeaderboardModel.score.desc()).offset(skip).limit(limit).all()

def update_leaderboard_entry_in_db(db: Session, leaderboard_id: int, leaderboard_data: Dict) -> Optional[LeaderboardModel]:
    db_leaderboard_entry = read_leaderboard_entry_from_db(db, leaderboard_id)
    if db_leaderboard_entry:
        for key, value in leaderboard_data.items():
            setattr(db_leaderboard_entry, key, value)
        db.commit()
        db.refresh(db_leaderboard_entry)
    return db_leaderboard_entry

def delete_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> bool:
    db_leaderboard_entry = read_leaderboard_entry_from_db(db, leaderboard_id)
    if db_leaderboard_entry:
        db.delete(db_leaderboard_entry)
        db.commit()
        return True
    return False

def read_or_create_time_period_in_db(db: Session, time_period_data: Dict) -> TimePeriodModel:
    db_time_period = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_data['id']).first()
    if not db_time_period:
        db_time_period = TimePeriodModel(**time_period_data)
        db.add(db_time_period)
        db.commit()
        db.refresh(db_time_period)
    return db_time_period

def read_leaderboard_entries_for_user_from_db(db: Session, user_id: int) -> List[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.user_id == user_id).all()

def read_leaderboard_entries_for_group_from_db(db: Session, group_id: int) -> List[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.group_id == group_id).all()
