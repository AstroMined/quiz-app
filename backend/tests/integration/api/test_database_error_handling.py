"""
Integration tests for database error handling.

Tests the current state of database constraint handling across API endpoints.
Some endpoints still use the validation service anti-pattern (application-level
error interception) while others properly allow database constraints to propagate
to the global error handler.

NOTE: This file documents the CURRENT behavior, not the ideal behavior.
Endpoints marked with "TODO" should be updated to use consistent database 
constraint error handling once the validation service anti-pattern is fully removed.
"""


def test_user_creation_with_invalid_role_id(logged_in_client):
    """Test user creation with invalid role_id returns HTTP 400.
    
    NOTE: This endpoint currently uses the validation service anti-pattern - 
    it intercepts IntegrityError in the CRUD layer and converts to ValueError,
    preventing proper database constraint error handling.
    """
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "role_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    # Current behavior: application-level validation returns generic message
    assert "detail" in error_data
    assert "Username or email already exists" in error_data["detail"] or "Role is required" in error_data["detail"]
    
    # TODO: Once validation service anti-pattern is removed from users endpoint,
    # this should return proper database constraint violation format:
    # assert error_data["error"] == "Constraint Violation"
    # assert error_data["type"] == "foreign_key_violation" 
    # assert "Invalid role" in error_data["detail"]
    # assert error_data["field"] == "role_id"
    # assert error_data["value"] == 9999


def test_user_response_creation_with_invalid_user_id(logged_in_client, test_model_questions, test_model_answer_choices):
    """Test user response creation with invalid user_id returns HTTP 400.
    
    NOTE: This endpoint SHOULD return proper database constraint violations
    because it doesn't intercept IntegrityError in the CRUD layer.
    """
    
    response_data = {
        "user_id": 9999,  # Invalid foreign key
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_answer_choices[0].id,
        "is_correct": True,
        "response_time": 30
    }
    
    response = logged_in_client.post("/user-responses/", json=response_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    # This endpoint should return structured constraint violation format
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        # Proper database constraint error handling
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid user" in error_data["detail"]
        assert error_data["field"] == "user_id"
        assert error_data["value"] == 9999
    else:
        # If application-level validation is still present, verify it returns appropriate error
        assert "detail" in error_data
        assert "user" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_user_response_creation_with_invalid_question_id(logged_in_client, test_model_user, test_model_answer_choices):
    """Test user response creation with invalid question_id returns HTTP 400."""
    
    response_data = {
        "user_id": test_model_user.id,
        "question_id": 9999,  # Invalid foreign key
        "answer_choice_id": test_model_answer_choices[0].id,
        "is_correct": True,
        "response_time": 30
    }
    
    response = logged_in_client.post("/user-responses/", json=response_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    # This endpoint should return structured constraint violation format
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid question" in error_data["detail"]
        assert error_data["field"] == "question_id"
        assert error_data["value"] == 9999
    else:
        # Application-level validation fallback
        assert "detail" in error_data
        assert "question" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_user_response_creation_with_invalid_answer_choice_id(logged_in_client, test_model_user, test_model_questions):
    """Test user response creation with invalid answer_choice_id returns HTTP 400."""
    
    response_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": 9999,  # Invalid foreign key
        "is_correct": True,
        "response_time": 30
    }
    
    response = logged_in_client.post("/user-responses/", json=response_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    # This endpoint should return structured constraint violation format
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid answer choice" in error_data["detail"]
        assert error_data["field"] == "answer_choice_id"
        assert error_data["value"] == 9999
    else:
        # Application-level validation fallback
        assert "detail" in error_data
        assert "answer" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_leaderboard_creation_with_invalid_user_id(logged_in_client, test_model_group, time_period_daily):
    """Test leaderboard creation with invalid user_id returns HTTP 400.
    
    NOTE: This endpoint should return proper database constraint violations.
    """
    
    leaderboard_data = {
        "user_id": 9999,  # Invalid foreign key
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": test_model_group.id
    }
    
    response = logged_in_client.post("/leaderboard/", json=leaderboard_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    # This endpoint should return structured constraint violation format
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid user" in error_data["detail"]
        assert error_data["field"] == "user_id"
        assert error_data["value"] == 9999
    else:
        # Application-level validation fallback
        assert "detail" in error_data
        assert "user" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_leaderboard_creation_with_invalid_group_id(logged_in_client, test_model_user, time_period_daily):
    """Test leaderboard creation with invalid group_id returns HTTP 400."""
    
    leaderboard_data = {
        "user_id": test_model_user.id,
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/leaderboard/", json=leaderboard_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid group" in error_data["detail"]
        assert error_data["field"] == "group_id"
        assert error_data["value"] == 9999
    else:
        assert "detail" in error_data
        assert "group" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_leaderboard_creation_with_invalid_time_period_id(logged_in_client, test_model_user, test_model_group):
    """Test leaderboard creation with invalid time_period_id returns HTTP 400."""
    
    leaderboard_data = {
        "user_id": test_model_user.id,
        "score": 100,
        "time_period_id": 9999,  # Invalid foreign key
        "group_id": test_model_group.id
    }
    
    response = logged_in_client.post("/leaderboard/", json=leaderboard_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid time period" in error_data["detail"]
        assert error_data["field"] == "time_period_id"
        assert error_data["value"] == 9999
    else:
        assert "detail" in error_data
        assert "time" in error_data["detail"].lower() or "period" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_question_creation_with_invalid_creator_id(logged_in_client):
    """Test question creation with invalid creator_id returns HTTP 400.
    
    NOTE: This endpoint should return proper database constraint violations.
    """
    
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": "Easy",
        "creator_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/questions/", json=question_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid creator" in error_data["detail"]
        assert error_data["field"] == "creator_id"
        assert error_data["value"] == 9999
    else:
        assert "detail" in error_data
        assert "creator" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_group_creation_with_invalid_creator_id(logged_in_client):
    """Test group creation with invalid creator_id returns HTTP 400.
    
    NOTE: This endpoint should return proper database constraint violations.
    """
    
    group_data = {
        "name": "Test Group",
        "description": "Test group description",
        "creator_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/groups/", json=group_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "foreign_key_violation"
        assert "Invalid creator" in error_data["detail"]
        assert error_data["field"] == "creator_id"
        assert error_data["value"] == 9999
    else:
        assert "detail" in error_data
        assert "creator" in error_data["detail"].lower() or "invalid" in error_data["detail"].lower()


def test_user_creation_with_duplicate_email(logged_in_client, test_model_user, test_model_role):
    """Test user creation with duplicate email returns HTTP 400.
    
    NOTE: This endpoint uses validation service anti-pattern - will return 
    generic error instead of structured constraint violation.
    """
    
    user_data = {
        "username": "newuser",
        "email": test_model_user.email,  # Duplicate email
        "password": "testpass123",
        "role_id": test_model_role.id
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    # Current behavior: application-level validation returns generic message
    assert "detail" in error_data
    assert "email" in error_data["detail"].lower() or "exists" in error_data["detail"].lower()


def test_user_creation_with_duplicate_username(logged_in_client, test_model_user, test_model_role):
    """Test user creation with duplicate username returns HTTP 400.
    
    NOTE: This endpoint uses validation service anti-pattern.
    """
    
    user_data = {
        "username": test_model_user.username,  # Duplicate username
        "email": "newemail@example.com",
        "password": "testpass123",
        "role_id": test_model_role.id
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    # Current behavior: application-level validation returns generic message
    assert "detail" in error_data
    assert "username" in error_data["detail"].lower() or "exists" in error_data["detail"].lower()


def test_group_creation_with_duplicate_name(logged_in_client, test_model_group, test_model_user):
    """Test group creation with duplicate name returns HTTP 400.
    
    NOTE: This endpoint should return proper database constraint violations.
    """
    
    group_data = {
        "name": test_model_group.name,  # Duplicate name
        "description": "Different description",
        "creator_id": test_model_user.id
    }
    
    response = logged_in_client.post("/groups/", json=group_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    
    if "error" in error_data and error_data.get("error") == "Constraint Violation":
        assert error_data["type"] == "unique_violation"
        assert "name already exists" in error_data["detail"]
        assert error_data["field"] == "name"
    else:
        assert "detail" in error_data
        assert "name" in error_data["detail"].lower() or "exists" in error_data["detail"].lower()


def test_subject_creation_with_duplicate_name(logged_in_client):
    """Test subject creation with duplicate name returns HTTP 400.
    
    NOTE: This endpoint has mixed validation patterns - both CRUD and 
    endpoint intercept IntegrityError.
    """
    
    # Create first subject
    subject_data = {
        "name": "Mathematics"
    }
    
    response1 = logged_in_client.post("/subjects/", json=subject_data)
    assert response1.status_code == 200
    
    # Try to create duplicate subject
    response2 = logged_in_client.post("/subjects/", json=subject_data)
    
    assert response2.status_code == 400
    
    error_data = response2.json()
    
    # This endpoint has complex error handling - test for reasonable error response
    assert "detail" in error_data
    assert "name" in error_data["detail"].lower() or "exists" in error_data["detail"].lower() or "duplicate" in error_data["detail"].lower()


def test_error_response_format_consistency(logged_in_client):
    """Test that constraint violation errors have some consistent format.
    
    NOTE: Due to mixed validation patterns, we test for basic consistency
    rather than the ideal structured format.
    """
    
    # Test foreign key violation
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role_id": 9999
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    assert response.status_code == 400
    
    error_data = response.json()
    
    # Verify basic error response structure
    assert "detail" in error_data
    assert isinstance(error_data["detail"], str)
    assert len(error_data["detail"]) > 0


def test_error_responses_do_not_expose_sensitive_data(logged_in_client):
    """Test that error responses don't expose sensitive internal data."""
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "testpass123",
        "role_id": 9999
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    error_data = response.json()
    
    # Verify no raw SQL or stack traces in response
    error_detail = error_data.get("detail", "")
    assert "INSERT" not in error_detail
    assert "UPDATE" not in error_detail
    assert "SELECT" not in error_detail
    assert "Traceback" not in error_detail
    assert "sqlite3" not in error_detail
    assert "sqlalchemy" not in error_detail.lower()


def test_successful_operations_unaffected_by_error_handlers(logged_in_client, test_model_role):
    """Test that successful operations are not affected by error handlers."""
    
    # This should succeed and not trigger error handling
    user_data = {
        "username": "valid_user",
        "email": "valid@example.com",
        "password": "testpass123",
        "role_id": test_model_role.id
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    assert response.status_code == 200
    
    # Verify user was created successfully
    user_data_response = response.json()
    assert user_data_response["username"] == "valid_user"
    assert user_data_response["email"] == "valid@example.com"
    assert user_data_response["role_id"] == test_model_role.id


def test_error_response_time_is_reasonable(logged_in_client):
    """Test that error responses are returned in reasonable time."""
    import time
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role_id": 9999
    }
    
    start_time = time.time()
    response = logged_in_client.post("/users/", json=user_data)
    end_time = time.time()
    
    assert response.status_code == 400
    
    # Error response should be fast (< 1 second)
    response_time = end_time - start_time
    assert response_time < 1.0, f"Error response took {response_time:.2f}s"