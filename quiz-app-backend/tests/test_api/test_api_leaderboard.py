# filename: tests/test_api/test_api_leaderboard.py

from app.models.user_responses import UserResponseModel
from app.models.time_period import TimePeriodModel

def test_get_leaderboard_daily(
    logged_in_client,
    db_session,
    test_user_with_group,
    test_questions
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[0].id,
            answer_choice_id=test_questions[0].answer_choices[0].id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[1].id,
            answer_choice_id=test_questions[1].answer_choices[0].id,
            is_correct=False
        )
    )
    db_session.commit()

    response = logged_in_client.get("/leaderboard/?time_period=daily")
    print(response.json())
    assert response.status_code == 200
    leaderboard_data = response.json()
    assert len(leaderboard_data) == 1
    assert leaderboard_data[0]["user_id"] == test_user_with_group.id
    assert leaderboard_data[0]["score"] == 1
    assert leaderboard_data[0]["time_period"] == TimePeriodModel.DAILY.value

def test_get_leaderboard_weekly(
    logged_in_client,
    db_session,
    test_user_with_group,
    test_questions
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[0].id,
            answer_choice_id=test_questions[0].answer_choices[0].id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[1].id,
            answer_choice_id=test_questions[1].answer_choices[0].id,
            is_correct=False
        )
    )
    db_session.commit()
    
    group_id = test_user_with_group.groups[0].id
    response = logged_in_client.get(f"/leaderboard/?time_period=weekly&group_id={group_id}")
    assert response.status_code == 200
    leaderboard_data = response.json()
    assert len(leaderboard_data) == 1
    assert leaderboard_data[0]["user_id"] == test_user_with_group.id
    assert leaderboard_data[0]["score"] == 1
    assert leaderboard_data[0]["time_period"] == TimePeriodModel.WEEKLY.value
    assert leaderboard_data[0]["group_id"] == group_id
