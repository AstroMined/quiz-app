# filename: app/models/leaderboard.py

from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.time_period import TimePeriodModel


class LeaderboardModel(Base):
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    time_period = Column(Enum(TimePeriodModel))
    group_id = Column(Integer, ForeignKey("groups.id"))

# Define relationships after all classes have been defined
LeaderboardModel.user = relationship("UserModel", back_populates="leaderboards")
LeaderboardModel.group = relationship("GroupModel", back_populates="leaderboards")

