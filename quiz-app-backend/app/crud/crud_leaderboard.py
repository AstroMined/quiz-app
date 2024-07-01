# filename: app/crud/crud_leaderboard.py

from sqlalchemy.orm import Session
from app.models.leaderboard import LeaderboardModel
from app.models.time_period import TimePeriodModel


def create_leaderboard_entry_crud(db: Session, user_id: int, score: int, time_period: TimePeriodModel, group_id: int = None):
    db_leaderboard_entry = LeaderboardModel(user_id=user_id, score=score, time_period=time_period, group_id=group_id)
    db.add(db_leaderboard_entry)
    db.commit()
    db.refresh(db_leaderboard_entry)
    return db_leaderboard_entry

def read_leaderboard_crud(db: Session, time_period: TimePeriodModel, group_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(LeaderboardModel).filter(LeaderboardModel.time_period == time_period)
    if group_id:
        query = query.filter(LeaderboardModel.group_id == group_id)
    return query.order_by(LeaderboardModel.score.desc()).offset(skip).limit(limit).all()

def update_leaderboard_entry_crud(db: Session, leaderboard_entry_id: int, score: int):
    db_leaderboard_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_entry_id).first()
    if db_leaderboard_entry:
        db_leaderboard_entry.score = score
        db.commit()
        db.refresh(db_leaderboard_entry)
    return db_leaderboard_entry

def delete_leaderboard_entry_crud(db: Session, leaderboard_entry_id: int):
    db_leaderboard_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_entry_id).first()
    if db_leaderboard_entry:
        db.delete(db_leaderboard_entry)
        db.commit()
    return db_leaderboard_entry
