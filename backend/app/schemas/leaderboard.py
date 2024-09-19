# filename: backend/app/schemas/leaderboard.py

from typing import Optional

from pydantic import BaseModel, Field

from backend.app.schemas.time_period import TimePeriodSchema


class LeaderboardBaseSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    score: int = Field(..., ge=0)
    group_id: Optional[int] = Field(None, gt=0)

class LeaderboardCreateSchema(LeaderboardBaseSchema):
    time_period_id: int = Field(..., gt=0)

class LeaderboardUpdateSchema(BaseModel):
    score: int = Field(..., ge=0)

class LeaderboardSchema(LeaderboardBaseSchema):
    id: int
    time_period_id: int
    time_period: TimePeriodSchema

    class Config:
        from_attributes = True
