# filename: tests/test_api_topics.py

from app.schemas import TopicCreateSchema

def test_create_topic(logged_in_client, db_session):
    # Create a test subject
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()

    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    response = logged_in_client.post("/topics/", json=topic_data.dict())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_read_topic(logged_in_client, db_session):
    # Create a test subject and topic
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.dict()).json()

    # Read the created topic
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_update_topic(logged_in_client, db_session):
    # Create a test subject and topic
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.dict()).json()

    # Update the topic
    updated_data = {"name": "Updated Topic", "subject_id": created_subject["id"]}
    response = logged_in_client.put(f"/topics/{created_topic['id']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_delete_topic(logged_in_client, db_session):
    # Create a test subject and topic
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.dict()).json()

    # Delete the topic
    response = logged_in_client.delete(f"/topics/{created_topic['id']}")
    assert response.status_code == 204

    # Check if the topic was deleted
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 404
