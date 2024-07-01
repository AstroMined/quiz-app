# filename: app/schemas/leaderboard.py

from typing import Optional
from pydantic import BaseModel
from app.models.time_period import TimePeriodModel
from app.services.logging_service import logger


class LeaderboardSchema(BaseModel):
    id: int
    user_id: int
    score: int
    time_period: TimePeriodModel
    group_id: Optional[int] = None

    class Config:
        from_attributes = True

