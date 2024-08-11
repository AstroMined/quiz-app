# filename: tests/test_services/test_scoring_service.py

import pytest
from app.services.scoring_service import calculate_user_score, calculate_leaderboard_scores
from app.models.time_period import TimePeriodModel
from app.crud.crud_user_responses import create_user_response_crud, get_user_responses_crud
from app.schemas.user_responses import UserResponseCreateSchema
from app.services.logging_service import logger

def test_calculate_user_score(
    db_session,
    test_model_user,
    test_model_questions
):
    logger.info(f"Starting test_calculate_user_score with {len(test_model_questions)} questions")
    
    # Create user responses for multiple questions using CRUD function
    for i, question in enumerate(test_model_questions):
        is_correct = i != 1  # Make the second answer incorrect, others correct
        user_response_data = UserResponseCreateSchema(
            user_id=test_model_user.id,
            question_id=question.id,
            answer_choice_id=question.answer_choices[0].id,
            is_correct=is_correct
        )
        created_response = create_user_response_crud(db=db_session, user_response=user_response_data)
        logger.info(f"Created user response: {created_response}")

    # Verify the created responses
    user_responses = get_user_responses_crud(db_session, user_id=test_model_user.id)
    logger.info(f"Retrieved user responses: {user_responses}")
    
    # Calculate the user's score
    user_score = calculate_user_score(test_model_user.id, db_session)
    logger.info(f"Calculated user score: {user_score}")
    
    # We expect correct answers for all questions except the second one
    expected_score = len(test_model_questions) - 1
    assert user_score == expected_score, f"Expected score of {expected_score}, but got {user_score}"
    logger.info(f"Test passed: User score {user_score} matches expected score {expected_score}")

def test_calculate_leaderboard_scores(
    db_session,
    test_model_user,
    test_model_questions
):
    # Create user responses for multiple questions using CRUD function
    for i, question in enumerate(test_model_questions[:2]):  # Use the first two questions
        is_correct = i == 0  # First answer is correct, second is incorrect
        user_response_data = UserResponseCreateSchema(
            user_id=test_model_user.id,
            question_id=question.id,
            answer_choice_id=question.answer_choices[0].id,
            is_correct=is_correct
        )
        create_user_response_crud(db=db_session, user_response=user_response_data)

    # Test daily leaderboard
    daily_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.DAILY)
    assert daily_scores == {test_model_user.id: 1}
    logger.debug(f"Daily leaderboard scores: {daily_scores}")

    # Test weekly leaderboard
    weekly_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.WEEKLY)
    assert weekly_scores == {test_model_user.id: 1}
    logger.debug(f"Weekly leaderboard scores: {weekly_scores}")

    # Test monthly leaderboard
    monthly_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.MONTHLY)
    assert monthly_scores == {test_model_user.id: 1}
    logger.debug(f"Monthly leaderboard scores: {monthly_scores}")

    # Test yearly leaderboard
    yearly_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.YEARLY)
    assert yearly_scores == {test_model_user.id: 1}
    logger.debug(f"Yearly leaderboard scores: {yearly_scores}")
