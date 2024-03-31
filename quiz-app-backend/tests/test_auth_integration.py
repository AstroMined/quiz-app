def test_protected_route_with_valid_token(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200

def test_protected_route_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401

def test_protected_route_with_revoked_token(client, test_user, test_token):
    """
    Test accessing a protected route with a revoked token.
    """
    # Logout to revoke the token
    headers = {"Authorization": f"Bearer {test_token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200
    
    # Try accessing the protected route with the revoked token
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]
