# filename: backend/tests/test_integration_cors.py

def test_cors_configuration(logged_in_client):
    response = logged_in_client.get("/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"