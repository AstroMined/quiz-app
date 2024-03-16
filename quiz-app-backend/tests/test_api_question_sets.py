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

def test_update_nonexistent_question_set(client, test_user):
    """
    Test updating a question set that does not exist.
    """
    question_set_update = {"name": "Updated Name"}
    response = client.put(f"/question-sets/99999", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_question_set_not_found(client, db_session):
    """
    Test updating a question set that does not exist.
    """
    question_set_id = 999  # Assuming this ID does not exist
    question_set_update = {"name": "Updated Name"}
    response = client.put(f"/question-sets/{question_set_id}", json=question_set_update)
    assert response.status_code == 404
    assert "Question set not found" in response.json()["detail"]

def test_delete_question_set_not_found(client, db_session):
    """
    Test deleting a question set that does not exist.
    """
    question_set_id = 999  # Assuming this ID does not exist
    response = client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 404
    assert "Question set not found" in response.json()["detail"]
