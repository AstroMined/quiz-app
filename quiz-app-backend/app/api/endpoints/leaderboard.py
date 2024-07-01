# filename: app/api/endpoints/leaderboard.py

# filename: app/api/endpoints/leaderboard.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.time_period import TimePeriodModel
from app.models.users import UserModel
from app.models.leaderboard import LeaderboardModel
from app.schemas.leaderboard import LeaderboardSchema
from app.services.scoring_service import calculate_leaderboard_scores
from app.services.user_service import get_current_user

router = APIRouter()

@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    time_period: TimePeriodModel,
    group_id: int = None,
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    leaderboard_scores = calculate_leaderboard_scores(db, time_period, group_id)
    leaderboard_data = [
        {
            "id": index + 1,
            "user_id": user_id,
            "score": score,
            "time_period": time_period,
            "group_id": group_id,
            "db": db
        }
        for index, (user_id, score) in enumerate(leaderboard_scores.items())
    ]
    leaderboard_schemas = [LeaderboardSchema(**data) for data in leaderboard_data]
    leaderboard_schemas.sort(key=lambda x: x.score, reverse=True)
    return leaderboard_schemas[:limit]
