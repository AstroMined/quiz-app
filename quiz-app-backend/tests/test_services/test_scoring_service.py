# filename: tests/test_scoring_service.py

from app.services.scoring_service import calculate_user_score, calculate_leaderboard_scores
from app.models.user_responses import UserResponseModel
from app.models.time_period import TimePeriodModel


def test_calculate_user_score(
    db_session,
    test_user,
    test_question,
    test_answer_choice_1,
    test_answer_choice_2
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_1.id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_2.id,
            is_correct=False
        )
    )
    db_session.commit()

    user_score = calculate_user_score(test_user.id, db_session)
    assert user_score == 1

def test_calculate_leaderboard_scores(
    db_session,
    test_user,
    test_question,
    test_answer_choice_1,
    test_answer_choice_2
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_1.id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_2.id,
            is_correct=False
        )
    )
    db_session.commit()

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.DAILY)
    assert leaderboard_scores == {test_user.id: 1}

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.WEEKLY)
    assert leaderboard_scores == {test_user.id: 1}

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.MONTHLY)
    assert leaderboard_scores == {test_user.id: 1}

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.YEARLY)
    assert leaderboard_scores == {test_user.id: 1}
