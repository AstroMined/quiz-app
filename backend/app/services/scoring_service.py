# filename: backend/app/services/scoring_service.py

from datetime import datetime, timedelta, timezone
from typing import Dict

from sqlalchemy.orm import Session

from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.time_period import TimePeriodModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.schemas.leaderboard import LeaderboardSchema, TimePeriodSchema
from backend.app.core.config import TimePeriod


def calculate_user_score(user_id: int, db: Session) -> int:
    user_responses = db.query(UserResponseModel).filter(UserResponseModel.user_id == user_id).all()
    total_score = sum(response.is_correct for response in user_responses)
    return total_score

def calculate_leaderboard_scores(
    db: Session,
    time_period: TimePeriodModel,
    group_id: int = None
) -> Dict[int, int]:
    user_scores = {}
    query = db.query(UserResponseModel)

    if time_period.id == TimePeriod.DAILY.value:
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
    elif time_period.id == TimePeriod.WEEKLY.value:
        start_time = datetime.now(timezone.utc) - timedelta(weeks=1)
    elif time_period.id == TimePeriod.MONTHLY.value:
        start_time = datetime.now(timezone.utc) - timedelta(days=30)
    elif time_period.id == TimePeriod.YEARLY.value:
        start_time = datetime.now(timezone.utc) - timedelta(days=365)
    else:
        start_time = None

    if start_time:
        query = query.filter(UserResponseModel.timestamp >= start_time)

    if group_id:
        query = query.join(UserModel).join(UserToGroupAssociation).filter(UserToGroupAssociation.group_id == group_id)

    user_responses = query.all()

    for response in user_responses:
        if response.user_id not in user_scores:
            user_scores[response.user_id] = 0
        if response.is_correct:
            user_scores[response.user_id] += 1

    return user_scores

def time_period_to_schema(time_period_model):
    return TimePeriodSchema(
        id=time_period_model.id,
        name=time_period_model.name
    )

def leaderboard_to_schema(leaderboard_model):
    return LeaderboardSchema(
        id=leaderboard_model.id,
        user_id=leaderboard_model.user_id,
        score=leaderboard_model.score,
        time_period=time_period_to_schema(leaderboard_model.time_period),
        group_id=leaderboard_model.group_id
    )