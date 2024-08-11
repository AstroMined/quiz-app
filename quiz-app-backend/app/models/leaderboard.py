# filename: app/models/leaderboard.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class LeaderboardModel(Base):
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    time_period_id = Column(Integer, ForeignKey("time_periods.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="leaderboards")
    group = relationship("GroupModel", back_populates="leaderboards")
    time_period = relationship("TimePeriodModel")

    def __repr__(self):
        return f"<LeaderboardModel(id={self.id}, user_id={self.user_id}, score={self.score}, time_period={self.time_period}, group_id={self.group_id})>"
