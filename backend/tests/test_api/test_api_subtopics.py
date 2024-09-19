import pytest
from fastapi import HTTPException

def test_create_subtopic(logged_in_client, test_model_topic):
    subtopic_data = {
        "name": "Test Subtopic",
        "topic_ids": [test_model_topic.id]
    }

    response = logged_in_client.post("/subtopics/", json=subtopic_data)
    assert response.status_code == 201
    created_subtopic = response.json()
    assert created_subtopic["name"] == "Test Subtopic"
    assert created_subtopic["topics"][0]["id"] == test_model_topic.id

def test_get_subtopics(logged_in_client, test_model_subtopic):
    response = logged_in_client.get("/subtopics/")
    assert response.status_code == 200
    subtopics = response.json()
    assert isinstance(subtopics, list)
    assert len(subtopics) >= 1

def test_get_subtopic(logged_in_client, test_model_subtopic):
    response = logged_in_client.get(f"/subtopics/{test_model_subtopic.id}")
    assert response.status_code == 200
    retrieved_subtopic = response.json()
    assert retrieved_subtopic["id"] == test_model_subtopic.id
    assert retrieved_subtopic["name"] == test_model_subtopic.name

def test_update_subtopic(logged_in_client, test_model_subtopic, test_model_topic):
    update_data = {
        "name": "Updated Subtopic",
        "topic_ids": [test_model_topic.id]
    }

    response = logged_in_client.put(f"/subtopics/{test_model_subtopic.id}", json=update_data)
    assert response.status_code == 200
    updated_subtopic = response.json()
    assert updated_subtopic["name"] == "Updated Subtopic"
    assert updated_subtopic["topics"][0]["id"] == test_model_topic.id

def test_delete_subtopic(logged_in_client, test_model_subtopic):
    response = logged_in_client.delete(f"/subtopics/{test_model_subtopic.id}")
    assert response.status_code == 204

    # Verify that the subtopic has been deleted
    get_response = logged_in_client.get(f"/subtopics/{test_model_subtopic.id}")
    assert get_response.status_code == 404

def test_create_subtopic_unauthorized(client, test_model_topic):
    subtopic_data = {
        "name": "Unauthorized Subtopic",
        "topic_ids": [test_model_topic.id]
    }
    with pytest.raises(HTTPException) as exc:
        client.post("/subtopics/", json=subtopic_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_subtopics_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/subtopics/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_nonexistent_subtopic(logged_in_client):
    response = logged_in_client.get("/subtopics/99999")
    assert response.status_code == 404

def test_update_nonexistent_subtopic(logged_in_client, test_model_topic):
    update_data = {
        "name": "Nonexistent Subtopic",
        "topic_ids": [test_model_topic.id]
    }
    response = logged_in_client.put("/subtopics/99999", json=update_data)
    assert response.status_code == 404

def test_delete_nonexistent_subtopic(logged_in_client):
    response = logged_in_client.delete("/subtopics/99999")
    assert response.status_code == 404