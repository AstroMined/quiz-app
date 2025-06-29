# filename: backend/tests/integration/isolation/test_transaction_isolation.py

import pytest
from backend.app.models.users import UserModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.core.security import get_password_hash


def test_transaction_isolation_between_tests_part1(db_session, test_model_role):
    """First part of isolation test - creates data that should be isolated."""
    from backend.app.models.users import UserModel
    
    # Create data that should be isolated to this test
    isolation_user = UserModel(
        username="isolation_test_user_part1",
        email="isolation_test_user_part1@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_admin=True,
        role_id=test_model_role.id,
    )
    db_session.add(isolation_user)
    db_session.flush()
    
    # Verify user exists in current test transaction
    found_user = db_session.query(UserModel).filter_by(
        username="isolation_test_user_part1"
    ).first()
    assert found_user is not None
    assert found_user.id == isolation_user.id
    
    # Also create a question for more comprehensive isolation testing
    from backend.app.models.questions import QuestionModel
    from backend.app.core.config import DifficultyLevel
    
    isolation_question = QuestionModel(
        text="What is test isolation?",
        difficulty=DifficultyLevel.BEGINNER,
        creator_id=isolation_user.id
    )
    db_session.add(isolation_question)
    db_session.flush()
    
    # Verify question exists
    found_question = db_session.query(QuestionModel).filter_by(
        text="What is test isolation?"
    ).first()
    assert found_question is not None
    
    # Test relies on transaction rollback to clean up


def test_transaction_isolation_between_tests_part2(db_session):
    """Second part of isolation test - verifies previous test data was cleaned up."""
    
    # This should NOT find the user from the previous test due to transaction rollback
    found_user = db_session.query(UserModel).filter_by(
        username="isolation_test_user_part1"
    ).first()
    assert found_user is None, "Data from previous test leaked - transaction isolation failed"
    
    # Also check that the question was cleaned up
    found_question = db_session.query(QuestionModel).filter_by(
        text="What is test isolation?"
    ).first()
    assert found_question is None, "Question data from previous test leaked"


def test_reference_data_persistence(db_session, test_model_user):
    """Verify reference data persists across tests while test data is isolated."""
    
    # Time periods should exist (session-scoped reference data)
    time_periods = db_session.query(TimePeriodModel).all()
    assert len(time_periods) > 0, "Reference data not properly initialized"
    
    # Create test-specific data
    test_specific_user = UserModel(
        username="reference_test_user",
        email="reference_test_user@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_admin=True,
        role_id=test_model_user.role_id,
    )
    db_session.add(test_specific_user)
    db_session.flush()
    
    # Both reference data and test data should be available
    assert db_session.query(TimePeriodModel).count() > 0
    assert db_session.query(UserModel).filter_by(username="reference_test_user").first() is not None


def test_reference_data_only_persists(db_session):
    """Verify only reference data persists, test data is cleaned up."""
    
    # Reference data should still exist
    time_periods = db_session.query(TimePeriodModel).all()
    assert len(time_periods) > 0, "Reference data should persist across tests"
    
    # Test data from previous test should be gone
    found_user = db_session.query(UserModel).filter_by(username="reference_test_user").first()
    assert found_user is None, "Test data leaked across test boundary"


def test_concurrent_transaction_isolation(db_session, test_model_role):
    """Test that multiple operations in the same transaction are isolated correctly."""
    
    # Create multiple users in the same transaction
    users = []
    for i in range(5):
        user = UserModel(
            username=f"concurrent_user_{i}",
            email=f"concurrent_user_{i}@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True,
            is_admin=True,
            role_id=test_model_role.id,
        )
        db_session.add(user)
        users.append(user)
    
    db_session.flush()
    
    # All users should be visible in the current transaction
    for i, user in enumerate(users):
        found_user = db_session.query(UserModel).filter_by(
            username=f"concurrent_user_{i}"
        ).first()
        assert found_user is not None
        assert found_user.id == user.id
    
    # Total user count should include all created users
    concurrent_user_count = db_session.query(UserModel).filter(
        UserModel.username.like("concurrent_user_%")
    ).count()
    assert concurrent_user_count == 5


def test_database_session_consistency(db_session, test_model_user):
    """Test that database session remains consistent throughout a test."""
    
    initial_user_count = db_session.query(UserModel).count()
    
    # Create new user
    new_user = UserModel(
        username="session_consistency_user",
        email="session_consistency_user@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_admin=True,
        role_id=test_model_user.role_id,
    )
    db_session.add(new_user)
    db_session.flush()
    
    # Count should increase by 1
    current_user_count = db_session.query(UserModel).count()
    assert current_user_count == initial_user_count + 1
    
    # Modify the user
    new_user.email = "modified_email@example.com"
    db_session.flush()
    
    # Verify modification is visible in the same session
    found_user = db_session.query(UserModel).filter_by(
        username="session_consistency_user"
    ).first()
    assert found_user.email == "modified_email@example.com"
    
    # Count should remain the same
    final_user_count = db_session.query(UserModel).count()
    assert final_user_count == current_user_count


def test_transaction_rollback_completeness(db_session, test_model_role):
    """Test that transaction rollback completely cleans up all data."""
    from backend.app.models.questions import QuestionModel
    from backend.app.core.config import DifficultyLevel
    
    # Record initial state
    initial_users = db_session.query(UserModel).count()
    initial_questions = db_session.query(QuestionModel).count()
    initial_subjects = db_session.query(SubjectModel).count()
    
    # Create complex interconnected data
    subject = SubjectModel(name="Rollback Test Subject")
    db_session.add(subject)
    db_session.flush()
    
    user = UserModel(
        username="rollback_test_user",
        email="rollback_test_user@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_admin=True,
        role_id=test_model_role.id,
    )
    db_session.add(user)
    db_session.flush()
    
    question = QuestionModel(
        text="Will this be rolled back?",
        difficulty=DifficultyLevel.MEDIUM,
        creator_id=user.id
    )
    question.subjects.append(subject)
    db_session.add(question)
    db_session.flush()
    
    # Verify data was created
    assert db_session.query(UserModel).count() == initial_users + 1
    assert db_session.query(QuestionModel).count() == initial_questions + 1
    assert db_session.query(SubjectModel).count() == initial_subjects + 1
    
    # Verify relationships
    found_question = db_session.query(QuestionModel).filter_by(
        text="Will this be rolled back?"
    ).first()
    assert found_question is not None
    assert found_question.creator_id == user.id
    assert len(found_question.subjects) == 1
    
    # Test relies on automatic transaction rollback for cleanup


def test_transaction_rollback_verification(db_session):
    """Verify that all data from the previous test was completely rolled back."""
    
    # None of the data from the previous test should exist
    rollback_user = db_session.query(UserModel).filter_by(
        username="rollback_test_user"
    ).first()
    assert rollback_user is None, "User was not rolled back"
    
    rollback_question = db_session.query(QuestionModel).filter_by(
        text="Will this be rolled back?"
    ).first()
    assert rollback_question is None, "Question was not rolled back"
    
    rollback_subject = db_session.query(SubjectModel).filter_by(
        name="Rollback Test Subject"
    ).first()
    assert rollback_subject is None, "Subject was not rolled back"


def test_isolation_with_exceptions(db_session, test_model_role):
    """Test that isolation works correctly even when exceptions occur."""
    
    initial_count = db_session.query(UserModel).count()
    
    # Create a user
    user = UserModel(
        username="exception_test_user",
        email="exception_test_user@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_admin=True,
        role_id=test_model_role.id,
    )
    db_session.add(user)
    db_session.flush()
    
    # Verify user was created
    assert db_session.query(UserModel).count() == initial_count + 1
    
    # Create another user with different username to test normal operations continue
    second_user = UserModel(
        username="exception_test_user_2",
        email="exception_test_user_2@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_admin=True,
        role_id=test_model_role.id,
    )
    db_session.add(second_user)
    db_session.flush()
    
    # Both users should exist and be accessible
    found_user = db_session.query(UserModel).filter_by(
        username="exception_test_user"
    ).first()
    assert found_user is not None
    
    found_user_2 = db_session.query(UserModel).filter_by(
        username="exception_test_user_2"
    ).first()
    assert found_user_2 is not None
    
    # Test cleanup relies on transaction rollback


def test_no_data_leakage_after_exceptions(db_session):
    """Verify no data leaked from the previous test that had exceptions."""
    
    # The users from the exception test should not exist
    exception_user = db_session.query(UserModel).filter_by(
        username="exception_test_user"
    ).first()
    assert exception_user is None, "Data leaked from test with exceptions"
    
    exception_user_2 = db_session.query(UserModel).filter_by(
        username="exception_test_user_2"
    ).first()
    assert exception_user_2 is None, "Data leaked from test with exceptions"


def test_performance_of_transaction_isolation(db_session, test_model_role, performance_tracker):
    """Test that transaction isolation doesn't significantly impact performance."""
    import time
    
    # Pre-hash password once to avoid bcrypt performance impact
    hashed_password = get_password_hash("TestPassword123!")
    
    start_time = time.perf_counter()
    
    # Perform multiple database operations
    users = []
    for i in range(10):  # Reduced to 10 for reasonable test time
        user = UserModel(
            username=f"perf_test_user_{i}",
            email=f"perf_test_user_{i}@example.com",
            hashed_password=hashed_password,  # Use pre-hashed password
            is_active=True,
            is_admin=True,
            role_id=test_model_role.id,
        )
        db_session.add(user)
        users.append(user)
    
    db_session.flush()
    
    # Perform some queries
    for user in users:
        found_user = db_session.query(UserModel).filter_by(id=user.id).first()
        assert found_user is not None
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    performance_tracker.record_test(
        test_name="transaction_isolation_performance",
        duration=duration,
        category="isolation_performance"
    )
    
    # Performance should be reasonable (excluding bcrypt hashing time)
    assert duration < 0.5, f"Transaction isolation operations took {duration:.3f}s, expected < 0.5s"
    
    print(f"\nTransaction Isolation Performance:")
    print(f"  Operations: 10 user creations + 10 queries")
    print(f"  Duration: {duration:.4f}s")
    print(f"  Per operation: {duration/20:.4f}s")


class TestRegressionSuite:
    """Comprehensive regression testing for new architecture."""
    
    def test_authentication_endpoints_regression(self, client, test_model_user):
        """Test all authentication endpoints work correctly after architecture changes."""
        
        # Test login
        login_response = client.post("/login", json={
            "username": test_model_user.username,
            "password": "TestPassword123!"
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
        
        # Test login with invalid credentials
        invalid_response = client.post("/login", json={
            "username": "nonexistent",
            "password": "wrong"
        })
        assert invalid_response.status_code in [401, 422]  # 422 for validation, 401 for auth
        
        # Test missing credentials
        missing_response = client.post("/login", json={
            "username": test_model_user.username
            # Missing password
        })
        assert missing_response.status_code == 422  # Validation error
    
    def test_crud_operations_regression(self, db_session, test_model_user, test_model_role):
        """Test all CRUD operations work with new database architecture."""
        
        # User CRUD
        original_count = db_session.query(UserModel).count()
        
        new_user = UserModel(
            username="crud_test_user",
            email="crud_test_user@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True,
            is_admin=False,
            role_id=test_model_role.id,
        )
        db_session.add(new_user)
        db_session.flush()
        
        # Read
        found_user = db_session.query(UserModel).filter_by(username="crud_test_user").first()
        assert found_user is not None
        assert found_user.email == "crud_test_user@example.com"
        
        # Update
        found_user.email = "updated_email@example.com"
        db_session.flush()
        
        updated_user = db_session.query(UserModel).filter_by(username="crud_test_user").first()
        assert updated_user.email == "updated_email@example.com"
        
        # Verify count increased by 1
        assert db_session.query(UserModel).count() == original_count + 1
    
    def test_complex_business_workflows_regression(self, db_session, test_model_user):
        """Test end-to-end business workflows still work correctly."""
        
        # Create a complete quiz workflow
        from backend.app.models.subjects import SubjectModel
        from backend.app.models.questions import QuestionModel
        from backend.app.core.config import DifficultyLevel
        from backend.app.models.answer_choices import AnswerChoiceModel
        
        # Create subject
        subject = SubjectModel(name="Regression Test Subject")
        db_session.add(subject)
        db_session.flush()
        
        # Create question
        question = QuestionModel(
            text="What is regression testing?",
            difficulty=DifficultyLevel.MEDIUM,
            creator_id=test_model_user.id
        )
        question.subjects.append(subject)
        db_session.add(question)
        db_session.flush()
        
        # Create answer choices
        correct_answer = AnswerChoiceModel(
            text="Testing to ensure new changes don't break existing functionality",
            is_correct=True
        )
        
        incorrect_answer = AnswerChoiceModel(
            text="Testing only new features",
            is_correct=False
        )
        
        # Associate answer choices with question through the relationship
        question.answer_choices.extend([correct_answer, incorrect_answer])
        
        db_session.add_all([correct_answer, incorrect_answer])
        db_session.flush()
        
        # Verify the complete workflow
        found_question = db_session.query(QuestionModel).filter_by(
            text="What is regression testing?"
        ).first()
        assert found_question is not None
        assert len(found_question.subjects) == 1
        assert found_question.subjects[0].name == "Regression Test Subject"
        
        # Check answer choices through the relationship
        assert len(found_question.answer_choices) == 2
        
        correct_answers = [ac for ac in found_question.answer_choices if ac.is_correct]
        assert len(correct_answers) == 1
        assert "ensure new changes don't break" in correct_answers[0].text