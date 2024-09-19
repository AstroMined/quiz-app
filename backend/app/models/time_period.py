# filename: backend/app/models/time_period.py

from sqlalchemy import Column, Integer, String

from backend.app.db.base import Base
from backend.app.core.config import TimePeriod


class TimePeriodModel(Base):
    __tablename__ = "time_periods"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(20), unique=True, nullable=False)

    @classmethod
    def create(cls, time_period: TimePeriod):
        return cls(id=time_period.value, name=time_period.get_name(time_period.value))

    def __repr__(self):
        return f"<TimePeriodModel(id={self.id}, name='{self.name}')"
