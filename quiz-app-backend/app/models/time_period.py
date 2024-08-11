# filename: app/models/time_period.py

from sqlalchemy import Column, Integer, String

from app.db.base import Base


class TimePeriodModel(Base):
    __tablename__ = "time_periods"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(20), unique=True, nullable=False)

    @classmethod
    def daily(cls):
        return cls(id=1, name="daily")

    @classmethod
    def weekly(cls):
        return cls(id=7, name="weekly")

    @classmethod
    def monthly(cls):
        return cls(id=30, name="monthly")

    @classmethod
    def yearly(cls):
        return cls(id=365, name="yearly")

    def __repr__(self):
        return f"<TimePeriodModel(id={self.id}, name='{self.name}')>"
