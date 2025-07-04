# filename: backend/tests/test_api_topics.py

import pytest
from fastapi import HTTPException

from backend.app.services.logging_service import logger


def test_create_topic(logged_in_client, test_model_subject):
    topic_data = {"name": "Test Topic", "subject_ids": [test_model_subject.id]}
    response = logged_in_client.post("/topics/", json=topic_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subjects"][0]["name"] == test_model_subject.name


def test_read_topic(logged_in_client, test_model_subject, test_model_topic):
    # Read the topic fixture
    response = logged_in_client.get(f"/topics/{test_model_topic.id}")
    logger.debug(response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subjects"][0]["id"] == test_model_subject.id


def test_update_topic(logged_in_client, test_model_subject):
    # Create a test topic
    topic_data = {"name": "Test Topic", "subject_ids": [test_model_subject.id]}
    created_topic = logged_in_client.post("/topics/", json=topic_data).json()

    # Update the topic
    updated_data = {"name": "Updated Topic", "subject_ids": [test_model_subject.id]}
    response = logged_in_client.put(f"/topics/{created_topic['id']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Topic"
    assert response.json()["subjects"][0]["id"] == test_model_subject.id


def test_delete_topic(logged_in_client, test_model_subject):
    # Create a test topic
    topic_data = {"name": "Test Topic", "subject_ids": [test_model_subject.id]}
    created_topic = logged_in_client.post("/topics/", json=topic_data).json()

    # Delete the topic
    response = logged_in_client.delete(f"/topics/{created_topic['id']}")
    assert response.status_code == 204

    # Check if the topic was deleted
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 404


def test_get_topics(logged_in_client, test_model_subject):
    # Create multiple test topics
    for i in range(3):
        topic_data = {"name": f"Test Topic {i}", "subject_ids": [test_model_subject.id]}
        logged_in_client.post("/topics/", json=topic_data)

    response = logged_in_client.get("/topics/")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) >= 3
    assert all(isinstance(topic, dict) for topic in topics)


def test_get_topics_pagination(logged_in_client, test_model_subject):
    # Create multiple test topics
    for i in range(10):
        topic_data = {"name": f"Test Topic {i}", "subject_ids": [test_model_subject.id]}
        logged_in_client.post("/topics/", json=topic_data)

    response = logged_in_client.get("/topics/?skip=5&limit=3")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) == 3


def test_create_topic_invalid_data(logged_in_client):
    invalid_topic_data = {"name": "", "subject_ids": []}
    response = logged_in_client.post("/topics/", json=invalid_topic_data)
    assert response.status_code == 422
    assert (
        "Topic name cannot be empty or whitespace"
        in response.json()["detail"][0]["msg"]
    )


def test_update_topic_not_found(logged_in_client, test_model_subject):
    update_data = {"name": "Updated Topic", "subject_ids": [test_model_subject.id]}
    response = logged_in_client.put("/topics/99999", json=update_data)
    assert response.status_code == 404
    assert "Topic not found" in response.json()["detail"]


def test_delete_topic_not_found(logged_in_client):
    response = logged_in_client.delete("/topics/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Topic not found"


def test_create_topic_unauthorized(client, test_model_subject):
    topic_data = {"name": "Unauthorized Topic", "subject_ids": [test_model_subject.id]}
    with pytest.raises(HTTPException) as exc:
        client.post("/topics/", json=topic_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_topics_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/topics/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_topic_unauthorized(client, test_model_topic):
    with pytest.raises(HTTPException) as exc:
        client.get(f"/topics/{test_model_topic.id}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_update_topic_unauthorized(client, test_model_topic, test_model_subject):
    update_data = {
        "name": "Unauthorized Update",
        "subject_ids": [test_model_subject.id],
    }
    with pytest.raises(HTTPException) as exc:
        client.put(f"/topics/{test_model_topic.id}", json=update_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_delete_topic_unauthorized(client, test_model_topic):
    with pytest.raises(HTTPException) as exc:
        client.delete(f"/topics/{test_model_topic.id}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_create_topic_duplicate_name(logged_in_client, test_model_subject):
    topic_data = {"name": "Duplicate Topic", "subject_ids": [test_model_subject.id]}

    # Create the first topic
    response = logged_in_client.post("/topics/", json=topic_data)
    assert response.status_code == 201

    # Try to create a topic with the same name
    response = logged_in_client.post("/topics/", json=topic_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_topic_no_changes(logged_in_client, test_model_topic):
    update_data = {
        "name": test_model_topic.name,
        "subject_ids": [s.id for s in test_model_topic.subjects],
    }
    response = logged_in_client.put(f"/topics/{test_model_topic.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == test_model_topic.name


def test_create_topic_long_name(logged_in_client, test_model_subject):
    long_name = "A" * 101  # Assuming max length is 100
    topic_data = {"name": long_name, "subject_ids": [test_model_subject.id]}
    response = logged_in_client.post("/topics/", json=topic_data)
    assert response.status_code == 422
    assert (
        "String should have at most 100 characters"
        in response.json()["detail"][0]["msg"]
    )


def test_update_topic_partial(logged_in_client, test_model_topic):
    update_data = {"name": "Partially Updated Topic"}
    response = logged_in_client.put(f"/topics/{test_model_topic.id}", json=update_data)
    assert response.status_code == 200
    updated_topic = response.json()
    assert updated_topic["name"] == "Partially Updated Topic"
    assert len(updated_topic["subjects"]) == len(test_model_topic.subjects)


def test_create_topic_non_existent_subject(logged_in_client):
    topic_data = {
        "name": "Invalid Subject Topic",
        "subject_ids": [99999],
    }  # Assuming 99999 is a non-existent subject ID
    response = logged_in_client.post("/topics/", json=topic_data)
    assert response.status_code == 422


def test_update_topic_non_existent_subject(logged_in_client, test_model_topic):
    update_data = {
        "name": "Invalid Subject Update",
        "subject_ids": [99999],
    }  # Assuming 99999 is a non-existent subject ID
    response = logged_in_client.put(f"/topics/{test_model_topic.id}", json=update_data)
    assert response.status_code == 404
    assert (
        "Topic not found or one or more subjects do not exist"
        in response.json()["detail"]
    )
