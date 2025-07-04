"""
Integration tests for direct database constraint violations.

Tests that database constraints properly trigger IntegrityError exceptions
when violated through direct SQLAlchemy operations.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from backend.app.models.users import UserModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.questions import QuestionModel
from backend.app.models.groups import GroupModel


def test_user_foreign_key_constraint_violation(db_session):
    """Test that invalid role_id triggers foreign key constraint violation."""
    
    # Create user with invalid role_id
    invalid_user = UserModel(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        role_id=99999  # Invalid foreign key
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_user)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_user_unique_constraint_violation_email(db_session, test_role):
    """Test that duplicate email triggers unique constraint violation."""
    
    # Create first user
    user1 = UserModel(
        username="user1",
        email="test@example.com",
        hashed_password="hash1",
        role_id=test_role.id
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create second user with same email
    user2 = UserModel(
        username="user2",
        email="test@example.com",  # Duplicate email
        hashed_password="hash2", 
        role_id=test_role.id
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(user2)
        db_session.commit()
    
    # Verify it's a unique constraint violation
    error_str = str(exc_info.value)
    assert "UNIQUE constraint failed" in error_str
    assert "users.email" in error_str


def test_user_unique_constraint_violation_username(db_session, test_role):
    """Test that duplicate username triggers unique constraint violation."""
    
    # Create first user
    user1 = UserModel(
        username="testuser",
        email="email1@example.com",
        hashed_password="hash1",
        role_id=test_role.id
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create second user with same username
    user2 = UserModel(
        username="testuser",  # Duplicate username
        email="email2@example.com",
        hashed_password="hash2",
        role_id=test_role.id
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(user2)
        db_session.commit()
    
    # Verify it's a unique constraint violation
    error_str = str(exc_info.value)
    assert "UNIQUE constraint failed" in error_str
    assert "users.username" in error_str


def test_user_response_foreign_key_constraint_user_id(db_session, test_questions, test_answer_choices):
    """Test that invalid user_id in user response triggers foreign key constraint."""
    
    # Create user response with invalid user_id
    invalid_response = UserResponseModel(
        user_id=99999,  # Invalid foreign key
        question_id=test_questions[0].id,
        answer_choice_id=test_answer_choices[0].id,
        is_correct=True,
        response_time=30
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_response)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_user_response_foreign_key_constraint_question_id(db_session, test_user, test_answer_choices):
    """Test that invalid question_id in user response triggers foreign key constraint."""
    
    # Create user response with invalid question_id
    invalid_response = UserResponseModel(
        user_id=test_user.id,
        question_id=99999,  # Invalid foreign key
        answer_choice_id=test_answer_choices[0].id,
        is_correct=True,
        response_time=30
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_response)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_user_response_foreign_key_constraint_answer_choice_id(db_session, test_user, test_questions):
    """Test that invalid answer_choice_id in user response triggers foreign key constraint."""
    
    # Create user response with invalid answer_choice_id
    invalid_response = UserResponseModel(
        user_id=test_user.id,
        question_id=test_questions[0].id,
        answer_choice_id=99999,  # Invalid foreign key
        is_correct=True,
        response_time=30
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_response)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_leaderboard_foreign_key_constraint_user_id(db_session, test_group, time_period_daily):
    """Test that invalid user_id in leaderboard triggers foreign key constraint."""
    
    # Create leaderboard entry with invalid user_id
    invalid_leaderboard = LeaderboardModel(
        user_id=99999,  # Invalid foreign key
        score=100,
        time_period_id=time_period_daily.id,
        group_id=test_group.id
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_leaderboard)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_leaderboard_foreign_key_constraint_group_id(db_session, test_user, time_period_daily):
    """Test that invalid group_id in leaderboard triggers foreign key constraint."""
    
    # Create leaderboard entry with invalid group_id
    invalid_leaderboard = LeaderboardModel(
        user_id=test_user.id,
        score=100,
        time_period_id=time_period_daily.id,
        group_id=99999  # Invalid foreign key
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_leaderboard)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_leaderboard_foreign_key_constraint_time_period_id(db_session, test_user, test_group):
    """Test that invalid time_period_id in leaderboard triggers foreign key constraint."""
    
    # Create leaderboard entry with invalid time_period_id
    invalid_leaderboard = LeaderboardModel(
        user_id=test_user.id,
        score=100,
        time_period_id=99999,  # Invalid foreign key
        group_id=test_group.id
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_leaderboard)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_question_foreign_key_constraint_creator_id(db_session):
    """Test that invalid creator_id in question triggers foreign key constraint."""
    
    # Create question with invalid creator_id
    invalid_question = QuestionModel(
        text="What is the capital of France?",
        difficulty="Easy",
        creator_id=99999  # Invalid foreign key
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_question)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_group_foreign_key_constraint_creator_id(db_session):
    """Test that invalid creator_id in group triggers foreign key constraint."""
    
    # Create group with invalid creator_id
    invalid_group = GroupModel(
        name="Test Group",
        description="Test group description",
        creator_id=99999  # Invalid foreign key
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(invalid_group)
        db_session.commit()
    
    # Verify it's a foreign key constraint violation
    error_str = str(exc_info.value)
    assert "FOREIGN KEY constraint failed" in error_str


def test_group_unique_constraint_violation_name(db_session, test_user):
    """Test that duplicate group name triggers unique constraint violation."""
    
    # Create first group
    group1 = GroupModel(
        name="Test Group",
        description="First description",
        creator_id=test_user.id
    )
    db_session.add(group1)
    db_session.commit()
    
    # Try to create second group with same name
    group2 = GroupModel(
        name="Test Group",  # Duplicate name
        description="Second description",
        creator_id=test_user.id
    )
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.add(group2)
        db_session.commit()
    
    # Verify it's a unique constraint violation
    error_str = str(exc_info.value)
    assert "UNIQUE constraint failed" in error_str
    assert "groups.name" in error_str


def test_constraint_violation_rollback_behavior(db_session, test_role):
    """Test that constraint violations properly rollback transactions."""
    
    # Get initial user count
    initial_count = db_session.query(UserModel).count()
    
    # Create valid user first
    valid_user = UserModel(
        username="validuser",
        email="valid@example.com",
        hashed_password="validhash",
        role_id=test_role.id
    )
    db_session.add(valid_user)
    
    # Try to create invalid user in same transaction
    invalid_user = UserModel(
        username="invaliduser",
        email="invalid@example.com",
        hashed_password="invalidhash",
        role_id=99999  # Invalid foreign key
    )
    db_session.add(invalid_user)
    
    # Transaction should fail and rollback
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    # Rollback the failed transaction
    db_session.rollback()
    
    # Verify no users were added due to rollback
    final_count = db_session.query(UserModel).count()
    assert final_count == initial_count, "Transaction should have been rolled back completely"


def test_constraint_performance_impact(db_session, test_role, performance_tracker):
    """Test that constraint violations don't significantly impact performance."""
    import time
    
    # Test multiple constraint violations to measure performance
    for i in range(10):
        start_time = time.perf_counter()
        
        # Create user with invalid role_id
        invalid_user = UserModel(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            hashed_password="hash",
            role_id=99999
        )
        
        try:
            db_session.add(invalid_user)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        # Record performance
        performance_tracker.record_test(
            test_name=f"constraint_violation_{i}",
            duration=duration,
            category="constraint_performance"
        )
        
        # Constraint violations should still be fast (< 0.1s)
        assert duration < 0.1, f"Constraint violation handling took {duration:.3f}s - too slow"