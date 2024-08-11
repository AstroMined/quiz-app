# filename: tests/test_api_subjects.py

from app.schemas.subjects import SubjectCreateSchema
from app.services.logging_service import logger


def test_create_subject(logged_in_client, test_model_discipline):
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_model_discipline.id)
    response = logged_in_client.post("/subjects/", json=subject_data.model_dump())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Subject"

def test_read_subject(logged_in_client, test_model_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_model_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()

    # Read the created subject
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Subject"

def test_update_subject(logged_in_client, test_model_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_model_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()

    # Update the subject
    updated_data = {"name": "Updated Subject"}
    response = logged_in_client.put(f"/subjects/{created_subject['id']}", json=updated_data)
    logger.debug(response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Subject"

def test_delete_subject(logged_in_client, test_model_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_model_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()

    # Delete the subject
    response = logged_in_client.delete(f"/subjects/{created_subject['id']}")
    assert response.status_code == 204

    # Check if the subject was deleted
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 404