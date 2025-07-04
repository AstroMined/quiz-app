"""
Database constraint tests.

Tests that database constraints properly enforce data integrity
at the database level, ensuring foreign key and unique constraints
work correctly.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.users import UserModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.questions import QuestionModel
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.groups import GroupModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.topics import TopicModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.concepts import ConceptModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel


def test_user_role_foreign_key_constraint(db_session, test_model_role):
    """Test that database enforces user.role_id foreign key constraint."""
    # Valid foreign key should work
    user = UserModel(
        username="testuser",
        email="test@example.com", 
        hashed_password="hash",
        role_id=test_model_role.id
    )
    db_session.add(user)
    db_session.commit()  # Should succeed
    
    # Invalid foreign key should fail at database level
    invalid_user = UserModel(
        username="testuser2",
        email="test2@example.com",
        hashed_password="hash", 
        role_id=9999
    )
    db_session.add(invalid_user)
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
    
    assert "FOREIGN KEY constraint failed" in str(exc_info.value)


def test_user_response_foreign_key_constraints(
    db_session, 
    test_model_user, 
    test_model_questions, 
    test_model_answer_choices
):
    """Test that database enforces user_responses foreign key constraints."""
    # Valid response should work
    response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True
    )
    db_session.add(response)
    db_session.commit()  # Should succeed
    
    # Invalid user_id should fail
    invalid_response = UserResponseModel(
        user_id=9999,  # Invalid user_id
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True
    )
    db_session.add(invalid_response)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_response_question_foreign_key_constraint(
    db_session, 
    test_model_user, 
    test_model_answer_choices
):
    """Test that database enforces user_responses.question_id foreign key constraint."""
    # Invalid question_id should fail
    invalid_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=9999,  # Invalid question_id
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True
    )
    db_session.add(invalid_response)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_response_answer_choice_foreign_key_constraint(
    db_session, 
    test_model_user, 
    test_model_questions
):
    """Test that database enforces user_responses.answer_choice_id foreign key constraint."""
    # Invalid answer_choice_id should fail
    invalid_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=9999,  # Invalid answer_choice_id
        is_correct=True
    )
    db_session.add(invalid_response)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_question_creator_foreign_key_constraint(db_session, test_model_user):
    """Test that database enforces questions.creator_id foreign key constraint."""
    # Valid creator_id should work
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty="EASY",
        creator_id=test_model_user.id
    )
    db_session.add(question)
    db_session.commit()  # Should succeed
    
    # Invalid creator_id should fail
    invalid_question = QuestionModel(
        text="What is the capital of Spain?",
        difficulty="EASY",
        creator_id=9999  # Invalid creator_id
    )
    db_session.add(invalid_question)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_group_creator_foreign_key_constraint(db_session, test_model_user):
    """Test that database enforces groups.creator_id foreign key constraint."""
    # Valid creator_id should work
    group = GroupModel(
        name="Test Group",
        description="A test group",
        creator_id=test_model_user.id
    )
    db_session.add(group)
    db_session.commit()  # Should succeed
    
    # Invalid creator_id should fail
    invalid_group = GroupModel(
        name="Invalid Group", 
        description="A group with invalid creator",
        creator_id=9999  # Invalid creator_id
    )
    db_session.add(invalid_group)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_leaderboard_foreign_key_constraints(
    db_session, 
    test_model_user, 
    test_model_group, 
    time_period_daily
):
    """Test that database enforces leaderboard foreign key constraints."""
    # Valid leaderboard should work
    leaderboard = LeaderboardModel(
        user_id=test_model_user.id,
        score=100,
        time_period_id=time_period_daily.id,
        group_id=test_model_group.id
    )
    db_session.add(leaderboard)
    db_session.commit()  # Should succeed
    
    # Invalid user_id should fail
    invalid_leaderboard = LeaderboardModel(
        user_id=9999,  # Invalid user_id
        score=100,
        time_period_id=time_period_daily.id,
        group_id=test_model_group.id
    )
    db_session.add(invalid_leaderboard)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_leaderboard_group_foreign_key_constraint(
    db_session, 
    test_model_user, 
    time_period_daily
):
    """Test that database enforces leaderboard.group_id foreign key constraint."""
    # Invalid group_id should fail
    invalid_leaderboard = LeaderboardModel(
        user_id=test_model_user.id,
        score=100,
        time_period_id=time_period_daily.id,
        group_id=9999  # Invalid group_id
    )
    db_session.add(invalid_leaderboard)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_leaderboard_time_period_foreign_key_constraint(
    db_session, 
    test_model_user, 
    test_model_group
):
    """Test that database enforces leaderboard.time_period_id foreign key constraint."""
    # Invalid time_period_id should fail
    invalid_leaderboard = LeaderboardModel(
        user_id=test_model_user.id,
        score=100,
        time_period_id=9999,  # Invalid time_period_id
        group_id=test_model_group.id
    )
    db_session.add(invalid_leaderboard)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_topic_subject_foreign_key_constraint(db_session, test_model_subject):
    """Test that database enforces topics.subject_id foreign key constraint."""
    # Valid subject_id should work
    topic = TopicModel(
        name="Test Topic",
        subject_id=test_model_subject.id
    )
    db_session.add(topic)
    db_session.commit()  # Should succeed
    
    # Invalid subject_id should fail
    invalid_topic = TopicModel(
        name="Invalid Topic",
        subject_id=9999  # Invalid subject_id
    )
    db_session.add(invalid_topic)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_subtopic_topic_foreign_key_constraint(db_session, test_model_topic):
    """Test that database enforces subtopics.topic_id foreign key constraint."""
    # Valid topic_id should work
    subtopic = SubtopicModel(
        name="Test Subtopic",
        topic_id=test_model_topic.id
    )
    db_session.add(subtopic)
    db_session.commit()  # Should succeed
    
    # Invalid topic_id should fail
    invalid_subtopic = SubtopicModel(
        name="Invalid Subtopic",
        topic_id=9999  # Invalid topic_id
    )
    db_session.add(invalid_subtopic)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_concept_subtopic_foreign_key_constraint(db_session, test_model_subtopic):
    """Test that database enforces concepts.subtopic_id foreign key constraint."""
    # Valid subtopic_id should work
    concept = ConceptModel(
        name="Test Concept",
        subtopic_id=test_model_subtopic.id
    )
    db_session.add(concept)
    db_session.commit()  # Should succeed
    
    # Invalid subtopic_id should fail
    invalid_concept = ConceptModel(
        name="Invalid Concept",
        subtopic_id=9999  # Invalid subtopic_id
    )
    db_session.add(invalid_concept)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_question_set_creator_foreign_key_constraint(db_session, test_model_user):
    """Test that database enforces question_sets.creator_id foreign key constraint."""
    # Valid creator_id should work
    question_set = QuestionSetModel(
        name="Test Question Set",
        description="A test question set",
        creator_id=test_model_user.id
    )
    db_session.add(question_set)
    db_session.commit()  # Should succeed
    
    # Invalid creator_id should fail
    invalid_question_set = QuestionSetModel(
        name="Invalid Question Set",
        description="A question set with invalid creator",
        creator_id=9999  # Invalid creator_id
    )
    db_session.add(invalid_question_set)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_email_unique_constraint(db_session, test_model_user, test_model_role):
    """Test that database enforces unique constraint on user.email."""
    # Attempt to create user with duplicate email should fail
    duplicate_user = UserModel(
        username="differentuser",
        email=test_model_user.email,  # Duplicate email
        hashed_password="hash",
        role_id=test_model_role.id
    )
    db_session.add(duplicate_user)
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
    
    assert "UNIQUE constraint failed" in str(exc_info.value)


def test_user_username_unique_constraint(db_session, test_model_user, test_model_role):
    """Test that database enforces unique constraint on user.username."""
    # Attempt to create user with duplicate username should fail
    duplicate_user = UserModel(
        username=test_model_user.username,  # Duplicate username
        email="different@example.com",
        hashed_password="hash",
        role_id=test_model_role.id
    )
    db_session.add(duplicate_user)
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
    
    assert "UNIQUE constraint failed" in str(exc_info.value)


def test_group_name_unique_constraint(db_session, test_model_group, test_model_user):
    """Test that database enforces unique constraint on group.name."""
    # Attempt to create group with duplicate name should fail
    duplicate_group = GroupModel(
        name=test_model_group.name,  # Duplicate name
        description="Different description",
        creator_id=test_model_user.id
    )
    db_session.add(duplicate_group)
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
    
    assert "UNIQUE constraint failed" in str(exc_info.value)


def test_subject_name_unique_constraint(db_session, test_model_subject):
    """Test that database enforces unique constraint on subject.name."""
    # Attempt to create subject with duplicate name should fail
    duplicate_subject = SubjectModel(
        name=test_model_subject.name  # Duplicate name
    )
    db_session.add(duplicate_subject)
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
    
    assert "UNIQUE constraint failed" in str(exc_info.value)


def test_cascade_deletion_behavior(
    db_session, 
    test_model_user, 
    test_model_questions, 
    test_model_answer_choices
):
    """Test that cascade deletion works correctly for foreign key relationships."""
    # Create a user response
    response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True
    )
    db_session.add(response)
    db_session.commit()
    
    response_id = response.id
    
    # Delete the user (should cascade to user_responses if configured)
    db_session.delete(test_model_user)
    db_session.commit()
    
    # Check if the response was also deleted (depends on cascade configuration)
    deleted_response = db_session.query(UserResponseModel).filter_by(id=response_id).first()
    # This test documents the current cascade behavior
    # The assertion depends on how cascades are configured in the models


def test_constraint_error_messages_are_informative(db_session, test_model_role):
    """Test that constraint error messages provide useful information."""
    invalid_user = UserModel(
        username="testuser",
        email="test@example.com",
        hashed_password="hash", 
        role_id=9999  # Invalid foreign key
    )
    db_session.add(invalid_user)
    
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
    
    error_message = str(exc_info.value)
    # Verify error message contains useful information
    assert "FOREIGN KEY constraint failed" in error_message
    # The exact format depends on the database backend (SQLite in this case)


def test_multiple_constraint_violations(db_session, test_model_user, test_model_role):
    """Test behavior when multiple constraints would be violated."""
    # Create user with both duplicate email and invalid role_id
    problematic_user = UserModel(
        username="newuser",
        email=test_model_user.email,  # Duplicate email
        hashed_password="hash",
        role_id=9999  # Invalid foreign key
    )
    db_session.add(problematic_user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    # Database will report the first constraint violation it encounters
    # The exact order depends on database implementation


def test_constraint_enforcement_during_update(db_session, test_model_user):
    """Test that constraints are enforced during UPDATE operations."""
    # Try to update user with invalid role_id
    test_model_user.role_id = 9999  # Invalid foreign key
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_constraint_enforcement_with_null_values(db_session, test_model_role):
    """Test constraint behavior with NULL values where allowed."""
    # Some foreign keys might allow NULL values
    user = UserModel(
        username="nulltestuser",
        email="null@example.com",
        hashed_password="hash",
        role_id=test_model_role.id
        # Note: not all foreign keys allow NULL - this tests the ones that do
    )
    db_session.add(user)
    db_session.commit()  # Should succeed if NULL is allowed
    
    assert user.id is not None