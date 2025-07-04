"""
Integration tests for database error handling.

Tests that constraint violations are properly caught and transformed
into user-friendly HTTP 400 responses across API endpoints.
"""


def test_user_creation_with_invalid_role_id(logged_in_client):
    """Test user creation with invalid role_id returns HTTP 400."""
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "role_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid role" in error_data["detail"]
    assert error_data["field"] == "role_id"
    assert error_data["value"] == 9999


def test_user_response_creation_with_invalid_user_id(logged_in_client, test_questions, test_answer_choices):
    """Test user response creation with invalid user_id returns HTTP 400."""
    
    response_data = {
        "user_id": 9999,  # Invalid foreign key
        "question_id": test_questions[0].id,
        "answer_choice_id": test_answer_choices[0].id,
        "is_correct": True,
        "response_time": 30
    }
    
    response = logged_in_client.post("/user-responses/", json=response_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid user" in error_data["detail"]
    assert error_data["field"] == "user_id"
    assert error_data["value"] == 9999


def test_user_response_creation_with_invalid_question_id(logged_in_client, test_user, test_answer_choices):
    """Test user response creation with invalid question_id returns HTTP 400."""
    
    response_data = {
        "user_id": test_user.id,
        "question_id": 9999,  # Invalid foreign key
        "answer_choice_id": test_answer_choices[0].id,
        "is_correct": True,
        "response_time": 30
    }
    
    response = logged_in_client.post("/user-responses/", json=response_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid question" in error_data["detail"]
    assert error_data["field"] == "question_id"
    assert error_data["value"] == 9999


def test_user_response_creation_with_invalid_answer_choice_id(logged_in_client, test_user, test_questions):
    """Test user response creation with invalid answer_choice_id returns HTTP 400."""
    
    response_data = {
        "user_id": test_user.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": 9999,  # Invalid foreign key
        "is_correct": True,
        "response_time": 30
    }
    
    response = logged_in_client.post("/user-responses/", json=response_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid answer choice" in error_data["detail"]
    assert error_data["field"] == "answer_choice_id"
    assert error_data["value"] == 9999


def test_leaderboard_creation_with_invalid_user_id(logged_in_client, test_group, time_period_daily):
    """Test leaderboard creation with invalid user_id returns HTTP 400."""
    
    leaderboard_data = {
        "user_id": 9999,  # Invalid foreign key
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": test_group.id
    }
    
    response = logged_in_client.post("/leaderboard/", json=leaderboard_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid user" in error_data["detail"]
    assert error_data["field"] == "user_id"
    assert error_data["value"] == 9999


def test_leaderboard_creation_with_invalid_group_id(logged_in_client, test_user, time_period_daily):
    """Test leaderboard creation with invalid group_id returns HTTP 400."""
    
    leaderboard_data = {
        "user_id": test_user.id,
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/leaderboard/", json=leaderboard_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid group" in error_data["detail"]
    assert error_data["field"] == "group_id"
    assert error_data["value"] == 9999


def test_leaderboard_creation_with_invalid_time_period_id(logged_in_client, test_user, test_group):
    """Test leaderboard creation with invalid time_period_id returns HTTP 400."""
    
    leaderboard_data = {
        "user_id": test_user.id,
        "score": 100,
        "time_period_id": 9999,  # Invalid foreign key
        "group_id": test_group.id
    }
    
    response = logged_in_client.post("/leaderboard/", json=leaderboard_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid time period" in error_data["detail"]
    assert error_data["field"] == "time_period_id"
    assert error_data["value"] == 9999


def test_question_creation_with_invalid_creator_id(logged_in_client):
    """Test question creation with invalid creator_id returns HTTP 400."""
    
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": "Easy",
        "creator_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/questions/", json=question_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid creator" in error_data["detail"]
    assert error_data["field"] == "creator_id"
    assert error_data["value"] == 9999


def test_group_creation_with_invalid_creator_id(logged_in_client):
    """Test group creation with invalid creator_id returns HTTP 400."""
    
    group_data = {
        "name": "Test Group",
        "description": "Test group description",
        "creator_id": 9999  # Invalid foreign key
    }
    
    response = logged_in_client.post("/groups/", json=group_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "foreign_key_violation"
    assert "Invalid creator" in error_data["detail"]
    assert error_data["field"] == "creator_id"
    assert error_data["value"] == 9999


def test_user_creation_with_duplicate_email(logged_in_client, test_user, test_role):
    """Test user creation with duplicate email returns HTTP 400."""
    
    user_data = {
        "username": "newuser",
        "email": test_user.email,  # Duplicate email
        "password": "testpass123",
        "role_id": test_role.id
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "unique_violation"
    assert "email already exists" in error_data["detail"]
    assert error_data["field"] == "email"


def test_user_creation_with_duplicate_username(logged_in_client, test_user, test_role):
    """Test user creation with duplicate username returns HTTP 400."""
    
    user_data = {
        "username": test_user.username,  # Duplicate username
        "email": "newemail@example.com",
        "password": "testpass123",
        "role_id": test_role.id
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "unique_violation"
    assert "username already exists" in error_data["detail"]
    assert error_data["field"] == "username"


def test_group_creation_with_duplicate_name(logged_in_client, test_group, test_user):
    """Test group creation with duplicate name returns HTTP 400."""
    
    group_data = {
        "name": test_group.name,  # Duplicate name
        "description": "Different description",
        "creator_id": test_user.id
    }
    
    response = logged_in_client.post("/groups/", json=group_data)
    
    assert response.status_code == 400
    
    error_data = response.json()
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "unique_violation"
    assert "name already exists" in error_data["detail"]
    assert error_data["field"] == "name"


def test_subject_creation_with_duplicate_name(logged_in_client):
    """Test subject creation with duplicate name returns HTTP 400."""
    
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
    assert error_data["error"] == "Constraint Violation"
    assert error_data["type"] == "unique_violation"
    assert "name already exists" in error_data["detail"]
    assert error_data["field"] == "name"


def test_error_response_format_consistency(logged_in_client):
    """Test that all constraint violation errors have consistent format."""
    
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
    
    # Verify required fields are present
    assert "error" in error_data
    assert "detail" in error_data
    assert "type" in error_data
    
    # Verify error field is consistent
    assert error_data["error"] == "Constraint Violation"
    
    # Verify type is appropriate
    assert error_data["type"] in [
        "foreign_key_violation",
        "unique_violation", 
        "check_violation",
        "constraint_violation"
    ]
    
    # Verify detail is a string
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
    assert "INSERT" not in error_data["detail"]
    assert "UPDATE" not in error_data["detail"]
    assert "SELECT" not in error_data["detail"]
    assert "Traceback" not in error_data["detail"]
    assert "sqlite3" not in error_data["detail"]
    assert "sqlalchemy" not in error_data["detail"]


def test_successful_operations_unaffected_by_error_handlers(logged_in_client, test_role):
    """Test that successful operations are not affected by error handlers."""
    
    # This should succeed and not trigger error handling
    user_data = {
        "username": "valid_user",
        "email": "valid@example.com",
        "password": "testpass123",
        "role_id": test_role.id
    }
    
    response = logged_in_client.post("/users/", json=user_data)
    
    assert response.status_code == 200
    
    # Verify user was created successfully
    user_data_response = response.json()
    assert user_data_response["username"] == "valid_user"
    assert user_data_response["email"] == "valid@example.com"
    assert user_data_response["role_id"] == test_role.id


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