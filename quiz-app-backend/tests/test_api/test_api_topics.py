# filename: tests/test_api_topics.py

from app.schemas.topics import TopicCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.services.logging_service import logger


def test_create_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)

    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    response = logged_in_client.post("/topics/", json=topic_data.model_dump())
    logger.debug("Response: %s", response.json())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_read_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.model_dump()).json()

    # Read the created topic
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_update_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.model_dump()).json()

    # Update the topic
    updated_data = {"name": "Updated Topic", "subject_id": created_subject["id"]}
    response = logged_in_client.put(f"/topics/{created_topic['id']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_delete_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.model_dump()).json()

    # Delete the topic
    response = logged_in_client.delete(f"/topics/{created_topic['id']}")
    assert response.status_code == 204

    # Check if the topic was deleted
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 404
