# filename: tests/test_api_question_sets.py
def test_create_question_set(client, db_session):
    data = {"name": "Test Question Set"}
    response = client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"

def test_read_question_sets(client, db_session, test_question_set):
    response = client.get("/question-sets/")
    assert response.status_code == 200
    assert any(qs["id"] == test_question_set.id and qs["name"] == test_question_set.name for qs in response.json())

# Add more tests for question set API endpoints