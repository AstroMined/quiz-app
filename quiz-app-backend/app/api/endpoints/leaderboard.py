# filename: app/api/endpoints/leaderboard.py

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.leaderboard import LeaderboardSchema, TimePeriodSchema
from app.services.scoring_service import calculate_leaderboard_scores, time_period_to_schema
from app.services.user_service import get_current_user
from app.models.time_period import TimePeriodModel

router = APIRouter()

@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    time_period: int = Query(..., description="Time period ID (1: daily, 7: weekly, 30: monthly, 365: yearly)"),
    group_id: int = None,
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    time_period_model = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period).first()
    if not time_period_model:
        raise ValueError("Invalid time period")

    leaderboard_scores = calculate_leaderboard_scores(db, time_period_model, group_id)
    leaderboard_data = [
        LeaderboardSchema(
            id=index + 1,
            user_id=user_id,
            score=score,
            time_period=time_period_to_schema(time_period_model),
            group_id=group_id
        )
        for index, (user_id, score) in enumerate(leaderboard_scores.items())
    ]
    leaderboard_data.sort(key=lambda x: x.score, reverse=True)
    return leaderboard_data[:limit]
