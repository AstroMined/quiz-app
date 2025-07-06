# filename: backend/tests/test_services/test_scoring_service.py

from datetime import datetime, timedelta, timezone
import uuid

import pytest

from backend.app.core.config import TimePeriod
from backend.app.core.security import get_password_hash
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.time_period import TimePeriodModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.models.questions import QuestionModel
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.groups import GroupModel
from backend.app.schemas.leaderboard import LeaderboardSchema, TimePeriodSchema
from backend.app.services.scoring_service import (
    calculate_leaderboard_scores,
    calculate_user_score,
    leaderboard_to_schema,
    time_period_to_schema,
)


def test_calculate_user_score(db_session, test_model_role):
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password=hashed_password,
        role_id=test_model_role.id,
    )
    db_session.add(user)
    db_session.commit()

    # Create test questions and answer choices
    question1 = QuestionModel(text="Test Question 1", difficulty="EASY")
    question2 = QuestionModel(text="Test Question 2", difficulty="EASY")
    db_session.add_all([question1, question2])
    db_session.flush()  # Get IDs
    
    answer1 = AnswerChoiceModel(text="Answer 1", is_correct=True)
    answer2 = AnswerChoiceModel(text="Answer 2", is_correct=False)
    db_session.add_all([answer1, answer2])
    db_session.flush()  # Get IDs
    
    # Associate answer choices with questions
    question1.answer_choices.append(answer1)
    question2.answer_choices.append(answer2)
    db_session.commit()

    # Create some test responses with required question_id and answer_choice_id
    responses = [
        UserResponseModel(user_id=user.id, question_id=question1.id, answer_choice_id=answer1.id, is_correct=True),
        UserResponseModel(user_id=user.id, question_id=question2.id, answer_choice_id=answer2.id, is_correct=False),
        UserResponseModel(user_id=user.id, question_id=question1.id, answer_choice_id=answer1.id, is_correct=True),
    ]
    db_session.add_all(responses)
    db_session.commit()

    # Calculate the score
    score = calculate_user_score(user.id, db_session)
    assert score == 2


def test_calculate_leaderboard_scores(db_session, test_model_role):
    # Create test users and groups
    hashed_password = get_password_hash("testpassword")
    unique_username1 = f"user1_{str(uuid.uuid4())[:8]}"
    unique_email1 = f"user1_{str(uuid.uuid4())[:8]}@example.com"
    unique_username2 = f"user2_{str(uuid.uuid4())[:8]}"
    unique_email2 = f"user2_{str(uuid.uuid4())[:8]}@example.com"
    
    user1 = UserModel(
        username=unique_username1,
        email=unique_email1,
        hashed_password=hashed_password,
        role_id=test_model_role.id,
    )
    user2 = UserModel(
        username=unique_username2,
        email=unique_email2,
        hashed_password=hashed_password,
        role_id=test_model_role.id,
    )
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create test group first
    test_group = GroupModel(name=f"test_group_{str(uuid.uuid4())[:8]}")
    db_session.add(test_group)
    db_session.commit()

    group = UserToGroupAssociation(user_id=user1.id, group_id=test_group.id)
    db_session.add(group)
    db_session.commit()

    # Create test questions and answer choices
    question1 = QuestionModel(text="Test Question 1", difficulty="EASY")
    question2 = QuestionModel(text="Test Question 2", difficulty="EASY")
    db_session.add_all([question1, question2])
    db_session.flush()  # Get IDs
    
    answer1 = AnswerChoiceModel(text="Answer 1", is_correct=True)
    answer2 = AnswerChoiceModel(text="Answer 2", is_correct=True)
    db_session.add_all([answer1, answer2])
    db_session.flush()  # Get IDs
    
    # Associate answer choices with questions
    question1.answer_choices.append(answer1)
    question2.answer_choices.append(answer2)
    db_session.commit()

    # Create test responses with required question_id and answer_choice_id
    now = datetime.now(timezone.utc)
    responses = [
        UserResponseModel(
            user_id=user1.id, question_id=question1.id, answer_choice_id=answer1.id, 
            is_correct=True, timestamp=now - timedelta(hours=1)
        ),
        UserResponseModel(
            user_id=user1.id, question_id=question2.id, answer_choice_id=answer2.id,
            is_correct=True, timestamp=now - timedelta(days=2)
        ),
        UserResponseModel(
            user_id=user2.id, question_id=question1.id, answer_choice_id=answer1.id,
            is_correct=True, timestamp=now - timedelta(hours=2)
        ),
    ]
    db_session.add_all(responses)
    db_session.commit()

    # Test daily leaderboard
    daily_scores = calculate_leaderboard_scores(
        db_session, TimePeriodModel(id=TimePeriod.DAILY.value)
    )
    # Filter results to only our test users to avoid contamination from other tests
    test_user_ids = {user1.id, user2.id}
    filtered_daily_scores = {user_id: score for user_id, score in daily_scores.items() if user_id in test_user_ids}
    assert filtered_daily_scores == {user1.id: 1, user2.id: 1}

    # Test weekly leaderboard
    weekly_scores = calculate_leaderboard_scores(
        db_session, TimePeriodModel(id=TimePeriod.WEEKLY.value)
    )
    # Filter results to only our test users to avoid contamination from other tests
    filtered_weekly_scores = {user_id: score for user_id, score in weekly_scores.items() if user_id in test_user_ids}
    assert filtered_weekly_scores == {user1.id: 2, user2.id: 1}

    # Test group leaderboard
    group_scores = calculate_leaderboard_scores(
        db_session, TimePeriodModel(id=TimePeriod.WEEKLY.value), group_id=test_group.id
    )
    # Filter results to only our test users to avoid contamination from other tests
    filtered_group_scores = {user_id: score for user_id, score in group_scores.items() if user_id in test_user_ids}
    assert filtered_group_scores == {user1.id: 2}


def test_time_period_to_schema():
    time_period_model = TimePeriodModel(id=1, name="daily")
    schema = time_period_to_schema(time_period_model)
    assert isinstance(schema, TimePeriodSchema)
    assert schema.id == 1
    assert schema.name == "daily"


def test_leaderboard_to_schema():
    time_period_model = TimePeriodModel(id=1, name="daily")
    leaderboard_model = type(
        "LeaderboardModel",
        (),
        {
            "id": 1,
            "user_id": 2,
            "score": 10,
            "time_period_id": 1,
            "time_period": time_period_model,
            "group_id": 3,
        },
    )()
    schema = leaderboard_to_schema(leaderboard_model)
    assert isinstance(schema, LeaderboardSchema)
    assert schema.id == 1
    assert schema.user_id == 2
    assert schema.score == 10
    assert schema.time_period.id == 1
    assert schema.time_period.name == "daily"
    assert schema.group_id == 3
