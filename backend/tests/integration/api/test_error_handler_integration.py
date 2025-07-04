"""
Integration tests for database error handler system.

Tests that error handlers are properly registered with FastAPI and
that error parsing functions work correctly in isolation.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from backend.app.api.error_handlers import parse_integrity_error, parse_foreign_key_error, get_foreign_key_message


def test_error_handler_registration(client):
    """Verify that IntegrityError handlers are registered with FastAPI app."""
    app = client.app
    
    # Check that exception handlers are registered
    handlers = getattr(app, '_exception_handlers', {})
    
    # Verify IntegrityError handler is registered
    assert IntegrityError in handlers, "IntegrityError handler not registered with FastAPI app"
    
    # Verify the handler is callable
    handler = handlers[IntegrityError]
    assert callable(handler), "IntegrityError handler is not callable"


def test_foreign_key_error_parsing():
    """Test parsing of foreign key constraint error messages."""
    
    # Test INSERT statement with foreign key violation
    insert_error = """(sqlite3.IntegrityError) FOREIGN KEY constraint failed
    [SQL: INSERT INTO users (username, email, hashed_password, role_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)]
    [parameters: ('testuser', 'test@example.com', 'hashedpass', 9999, '2024-01-01 00:00:00', '2024-01-01 00:00:00')]"""
    
    result = parse_integrity_error(insert_error)
    
    assert result["type"] == "foreign_key_violation"
    assert result["field"] == "role_id"
    assert result["value"] == 9999
    assert "Invalid role: 9999" in result["message"]


def test_unique_constraint_error_parsing():
    """Test parsing of unique constraint violation error messages."""
    
    # Test unique constraint on email
    unique_error = """(sqlite3.IntegrityError) UNIQUE constraint failed: users.email
    [SQL: INSERT INTO users (username, email, hashed_password, role_id) VALUES (?, ?, ?, ?)]"""
    
    result = parse_integrity_error(unique_error)
    
    assert result["type"] == "unique_violation"
    assert result["field"] == "email"
    assert "email already exists" in result["message"]


def test_unique_constraint_username_parsing():
    """Test parsing of unique constraint violation for username."""
    
    unique_error = """(sqlite3.IntegrityError) UNIQUE constraint failed: users.username
    [SQL: INSERT INTO users (username, email, hashed_password, role_id) VALUES (?, ?, ?, ?)]"""
    
    result = parse_integrity_error(unique_error)
    
    assert result["type"] == "unique_violation"
    assert result["field"] == "username"
    assert "username already exists" in result["message"]


def test_foreign_key_message_generation():
    """Test generation of user-friendly foreign key error messages."""
    
    # Test various foreign key fields
    test_cases = [
        ("role_id", "9999", "Invalid role: 9999"),
        ("user_id", "5555", "Invalid user: 5555"),
        ("question_id", "1234", "Invalid question: 1234"),
        ("answer_choice_id", "7777", "Invalid answer choice: 7777"),
        ("creator_id", "8888", "Invalid creator: 8888"),
        ("group_id", "3333", "Invalid group: 3333"),
        ("time_period_id", "2222", "Invalid time period: 2222")
    ]
    
    for field, value, expected_message in test_cases:
        message = get_foreign_key_message(field, value)
        assert message == expected_message, f"Unexpected message for {field}: {message}"


def test_foreign_key_error_parsing_direct():
    """Test foreign key error parsing function directly."""
    
    # Test UPDATE statement pattern
    update_error = """(sqlite3.IntegrityError) FOREIGN KEY constraint failed
    [SQL: UPDATE users SET role_id = ? WHERE users.id = ?]
    [parameters: (9999, 1)]"""
    
    result = parse_foreign_key_error(update_error)
    
    assert result["type"] == "foreign_key_violation"
    assert result["field"] == "role_id"
    assert result["value"] == 9999
    assert "Invalid role: 9999" in result["message"]


def test_generic_foreign_key_error_fallback():
    """Test fallback behavior for unparseable foreign key errors."""
    
    generic_error = "FOREIGN KEY constraint failed"
    
    result = parse_foreign_key_error(generic_error)
    
    assert result["type"] == "foreign_key_violation"
    assert result["message"] == "Invalid foreign key reference"
    assert "field" not in result
    assert "value" not in result


def test_generic_constraint_error_fallback():
    """Test fallback behavior for unknown constraint violations."""
    
    unknown_error = "Some unknown constraint violation"
    
    result = parse_integrity_error(unknown_error)
    
    assert result["type"] == "constraint_violation"
    assert result["message"] == "Database constraint violation occurred"


def test_check_constraint_error_parsing():
    """Test parsing of check constraint violations."""
    
    check_error = "CHECK constraint failed: difficulty_check"
    
    result = parse_integrity_error(check_error)
    
    assert result["type"] == "check_violation"
    assert "Invalid value" in result["message"]


def test_error_parsing_performance(performance_tracker):
    """Test that error parsing functions perform efficiently."""
    import time
    
    # Test data for performance measurement
    error_messages = [
        "FOREIGN KEY constraint failed",
        "UNIQUE constraint failed: users.email", 
        "CHECK constraint failed: difficulty_check",
        """(sqlite3.IntegrityError) FOREIGN KEY constraint failed
        [SQL: INSERT INTO users (username, email, hashed_password, role_id) VALUES (?, ?, ?, ?)]
        [parameters: ('test', 'test@example.com', 'hash', 9999)]"""
    ]
    
    # Measure parsing performance
    for i, error_msg in enumerate(error_messages):
        start_time = time.perf_counter()
        result = parse_integrity_error(error_msg)
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        
        # Record performance data
        performance_tracker.record_test(
            test_name=f"error_parsing_{i}",
            duration=duration,
            category="error_parsing"
        )
        
        # Verify result is valid
        assert "type" in result
        assert "message" in result
        
        # Assert performance target (parsing should be very fast)
        assert duration < 0.001, f"Error parsing took {duration:.6f}s - too slow"


def test_multiple_foreign_key_fields_parsing():
    """Test parsing when multiple foreign key fields are present."""
    
    multi_fk_error = """(sqlite3.IntegrityError) FOREIGN KEY constraint failed
    [SQL: INSERT INTO user_responses (user_id, question_id, answer_choice_id, is_correct, response_time) VALUES (?, ?, ?, ?, ?)]
    [parameters: (9999, 1, 1, True, 30)]"""
    
    result = parse_foreign_key_error(multi_fk_error)
    
    # Should pick the first foreign key field (user_id in this case)
    assert result["type"] == "foreign_key_violation"
    assert result["field"] == "user_id"
    assert result["value"] == 9999
    assert "Invalid user: 9999" in result["message"]