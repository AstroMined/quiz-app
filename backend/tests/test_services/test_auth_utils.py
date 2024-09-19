# filename: backend/tests/test_services/test_auth_utils.py

import pytest
from fastapi import HTTPException, Request
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

def create_mock_request(auth_status, current_user=None):
    class MockRequest:
        def __init__(self):
            self.state = type('State', (), {'auth_status': auth_status, 'current_user': current_user})()
    return MockRequest()

def test_check_auth_status_authorized():
    request = create_mock_request({"is_authorized": True})
    assert check_auth_status(request) is None

def test_check_auth_status_unauthorized():
    error_cases = [
        ("invalid_token", 401),
        ("token_expired", 401),
        ("revoked_token", 401),
        ("user_not_found", 401),
        ("invalid_token_format", 401),
        ("insufficient_permissions", 403),
        ("missing_token", 401),
        ("unexpected_error", 500),
    ]

    for error, expected_status_code in error_cases:
        request = create_mock_request({"is_authorized": False, "error": error})
        with pytest.raises(HTTPException) as exc_info:
            check_auth_status(request)
        assert exc_info.value.status_code == expected_status_code

def test_check_auth_status_missing():
    request = create_mock_request({})
    with pytest.raises(HTTPException) as exc_info:
        check_auth_status(request)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Authentication status not available"

def test_get_current_user_or_error_success():
    mock_user = {"id": 1, "username": "testuser"}
    request = create_mock_request({"is_authorized": True}, mock_user)
    assert get_current_user_or_error(request) == mock_user

def test_get_current_user_or_error_no_user():
    request = create_mock_request({"is_authorized": True}, None)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_or_error(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not authenticated"