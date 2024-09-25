# filename: backend/tests/test_integration_auth.py

import pytest
from fastapi import HTTPException


def test_protected_route_with_valid_token(client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200


def test_protected_route_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    # Try accessing the protected route with the invalid token
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_protected_route_with_revoked_token(client, test_token):
    # Logout to revoke the token
    headers = {"Authorization": f"Bearer {test_token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200

    # Try accessing the protected route with the revoked token
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
