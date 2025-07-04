"""
Unit tests for database error handlers.

Tests the error parsing functions and message generation without 
requiring database connections or FastAPI app context.
"""

from backend.app.api.error_handlers import (
    parse_integrity_error,
    parse_foreign_key_error,
    parse_check_constraint_error,
    get_foreign_key_message,
    get_unique_constraint_message
)


def test_parse_foreign_key_error_with_insert_statement():
    """Test parsing foreign key constraint violations from INSERT statements."""
    error_message = (
        "FOREIGN KEY constraint failed: "
        "INSERT INTO users (username, email, hashed_password, role_id) "
        "VALUES ('testuser', 'test@example.com', 'hash', 999)"
    )
    
    result = parse_integrity_error(error_message)
    
    assert result["type"] == "foreign_key_violation"
    assert result["field"] == "role_id"
    assert result["value"] == 999
    assert "Invalid role: 999" in result["message"]


def test_parse_unique_constraint_error():
    """Test parsing unique constraint violations."""
    error_message = "UNIQUE constraint failed: users.email"
    
    result = parse_integrity_error(error_message)
    
    assert result["type"] == "unique_violation"
    assert result["field"] == "email"
    assert result["message"] == "A user with this email already exists"


def test_parse_check_constraint_error():
    """Test parsing check constraint violations."""
    error_message = "CHECK constraint failed: difficulty_level_check"
    
    result = parse_integrity_error(error_message)
    
    assert result["type"] == "check_violation"
    assert result["constraint"] == "difficulty_level_check"
    assert "Invalid value for difficulty_level_check" in result["message"]


def test_parse_generic_constraint_error():
    """Test parsing unrecognized constraint violations."""
    error_message = "Some other constraint violation"
    
    result = parse_integrity_error(error_message)
    
    assert result["type"] == "constraint_violation"
    assert result["message"] == "Database constraint violation occurred"


def test_parse_foreign_key_from_insert_with_multiple_fields():
    """Test extracting field and value from INSERT statement with multiple foreign keys."""
    error_message = (
        "FOREIGN KEY constraint failed: "
        "INSERT INTO user_responses (user_id, question_id, answer_choice_id, is_correct) "
        "VALUES (1, 999, 1, True)"
    )
    
    result = parse_foreign_key_error(error_message)
    
    assert result["type"] == "foreign_key_violation"
    assert result["field"] == "user_id"
    assert result["value"] == 1
    assert "Invalid user: 1" in result["message"]


def test_parse_foreign_key_from_update_statement():
    """Test extracting field and value from UPDATE statement."""
    error_message = (
        "FOREIGN KEY constraint failed: "
        "UPDATE users SET role_id = 999 WHERE id = 1"
    )
    
    result = parse_foreign_key_error(error_message)
    
    assert result["type"] == "foreign_key_violation"
    assert result["field"] == "role_id"
    assert result["value"] == 999
    assert "Invalid role: 999" in result["message"]


def test_parse_generic_foreign_key_error():
    """Test parsing foreign key error without extractable details."""
    error_message = "FOREIGN KEY constraint failed"
    
    result = parse_foreign_key_error(error_message)
    
    assert result["type"] == "foreign_key_violation"
    assert result["message"] == "Invalid foreign key reference"
    assert "field" not in result
    assert "value" not in result


def test_parse_check_constraint_with_name():
    """Test parsing check constraint with constraint name."""
    error_message = "CHECK constraint failed: difficulty_level_check"
    
    result = parse_check_constraint_error(error_message)
    
    assert result["type"] == "check_violation"
    assert result["constraint"] == "difficulty_level_check"
    assert result["message"] == "Invalid value for difficulty_level_check"


def test_parse_check_constraint_without_name():
    """Test parsing check constraint without constraint name."""
    error_message = "CHECK constraint failed"
    
    result = parse_check_constraint_error(error_message)
    
    assert result["type"] == "check_violation"
    assert result["message"] == "Invalid value provided"
    assert "constraint" not in result


def test_get_foreign_key_message_for_role_id():
    """Test user-friendly message for role_id foreign key."""
    result = get_foreign_key_message("role_id", "123")
    assert result == "Invalid role: 123"


def test_get_foreign_key_message_for_user_id():
    """Test user-friendly message for user_id foreign key."""
    result = get_foreign_key_message("user_id", "456")
    assert result == "Invalid user: 456"


def test_get_foreign_key_message_for_question_id():
    """Test user-friendly message for question_id foreign key."""
    result = get_foreign_key_message("question_id", "789")
    assert result == "Invalid question: 789"


def test_get_foreign_key_message_for_answer_choice_id():
    """Test user-friendly message for answer_choice_id foreign key."""
    result = get_foreign_key_message("answer_choice_id", "101")
    assert result == "Invalid answer choice: 101"


def test_get_foreign_key_message_for_group_id():
    """Test user-friendly message for group_id foreign key."""
    result = get_foreign_key_message("group_id", "202")
    assert result == "Invalid group: 202"


def test_get_foreign_key_message_for_creator_id():
    """Test user-friendly message for creator_id foreign key."""
    result = get_foreign_key_message("creator_id", "404")
    assert result == "Invalid creator: 404"


def test_get_foreign_key_message_for_unknown_field():
    """Test handling of unknown foreign key fields."""
    result = get_foreign_key_message("unknown_field_id", "123")
    assert result == "Invalid unknown_field: 123"


def test_get_foreign_key_message_for_field_without_id_suffix():
    """Test handling of fields without _id suffix."""
    result = get_foreign_key_message("parent", "123")
    assert result == "Invalid parent: 123"


def test_get_unique_constraint_message_for_email():
    """Test user-friendly message for email unique constraint."""
    result = get_unique_constraint_message("email")
    assert result == "A user with this email already exists"


def test_get_unique_constraint_message_for_username():
    """Test user-friendly message for username unique constraint."""
    result = get_unique_constraint_message("username")
    assert result == "A user with this username already exists"


def test_get_unique_constraint_message_for_name():
    """Test user-friendly message for name unique constraint."""
    result = get_unique_constraint_message("name")
    assert result == "A record with this name already exists"


def test_get_unique_constraint_message_for_unknown_field():
    """Test generic message for unknown unique fields."""
    result = get_unique_constraint_message("some_field")
    assert result == "A record with this some_field already exists"


def test_empty_error_message():
    """Test handling of empty error messages."""
    result = parse_integrity_error("")
    
    assert result["type"] == "constraint_violation"
    assert result["message"] == "Database constraint violation occurred"


def test_malformed_unique_constraint_message():
    """Test handling of malformed unique constraint messages."""
    error_message = "UNIQUE constraint failed: invalid_format"
    
    result = parse_integrity_error(error_message)
    
    assert result["type"] == "constraint_violation"
    assert result["message"] == "Database constraint violation occurred"


def test_foreign_key_with_non_numeric_value():
    """Test foreign key parsing with non-numeric values."""
    error_message = (
        "FOREIGN KEY constraint failed: "
        "INSERT INTO users (role_id) VALUES ('not_a_number')"
    )
    
    result = parse_integrity_error(error_message)
    
    # Should fall back to generic foreign key error
    assert result["type"] == "foreign_key_violation"
    assert result["message"] == "Invalid foreign key reference"


def test_unique_constraint_with_complex_field_name():
    """Test unique constraint with complex table.field format."""
    error_message = "UNIQUE constraint failed: user_group_memberships.user_id_group_id"
    
    result = parse_integrity_error(error_message)
    
    assert result["type"] == "unique_violation"
    assert result["field"] == "user_id_group_id"
    assert "A record with this user_id_group_id already exists" in result["message"]