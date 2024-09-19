# filename: backend/tests/test_api_subjects.py

import pytest
from fastapi import HTTPException
from backend.app.services.logging_service import logger

def test_create_subject(logged_in_client, test_model_discipline):
    subject_data = {"name":"Test Subject", "discipline_ids":[test_model_discipline.id]}
    response = logged_in_client.post("/subjects/", json=subject_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Subject"

def test_read_subject(logged_in_client, test_model_discipline):
    # Create a test subject
    subject_data = {"name":"Test Subject", "discipline_ids":[test_model_discipline.id]}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()

    # Read the created subject
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    logger.debug(response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Test Subject"
    assert response.json()["disciplines"][0]["id"] == test_model_discipline.id

def test_update_subject(logged_in_client, test_model_subject):
    # Update the subject
    updated_data = {"name": "Updated Subject"}
    response = logged_in_client.put(f"/subjects/{test_model_subject.id}", json=updated_data)
    logger.debug(response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Subject"

def test_delete_subject(logged_in_client, test_model_discipline):
    # Create a test subject
    subject_data = {"name":"Test Subject", "discipline_ids":[test_model_discipline.id]}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()

    # Delete the subject
    response = logged_in_client.delete(f"/subjects/{created_subject['id']}")
    assert response.status_code == 204

    # Check if the subject was deleted
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 404

def test_get_subjects(logged_in_client, test_model_discipline):
    # Create multiple test subjects
    for i in range(3):
        subject_data = {"name": f"Test Subject {i}", "discipline_ids": [test_model_discipline.id]}
        logged_in_client.post("/subjects/", json=subject_data)

    response = logged_in_client.get("/subjects/")
    assert response.status_code == 200
    subjects = response.json()
    assert len(subjects) >= 3
    assert all(isinstance(subject, dict) for subject in subjects)

def test_get_subjects_pagination(logged_in_client, test_model_discipline):
    # Create multiple test subjects
    for i in range(10):
        subject_data = {"name": f"Test Subject {i}", "discipline_ids": [test_model_discipline.id]}
        logged_in_client.post("/subjects/", json=subject_data)

    response = logged_in_client.get("/subjects/?skip=5&limit=3")
    assert response.status_code == 200
    subjects = response.json()
    assert len(subjects) == 3

def test_create_subject_invalid_data(logged_in_client):
    invalid_subject_data = {"name": "", "discipline_ids": []}
    response = logged_in_client.post("/subjects/", json=invalid_subject_data)
    assert response.status_code == 422

def test_update_subject_not_found(logged_in_client):
    update_data = {"name": "Updated Subject"}
    response = logged_in_client.put("/subjects/99999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Subject not found"

def test_delete_subject_not_found(logged_in_client):
    response = logged_in_client.delete("/subjects/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Subject not found"

def test_create_subject_unauthorized(client, test_model_discipline):
    subject_data = {"name": "Unauthorized Subject", "discipline_ids": [test_model_discipline.id]}
    with pytest.raises(HTTPException) as exc:
        client.post("/subjects/", json=subject_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_subjects_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/subjects/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_subject_unauthorized(client, test_model_subject):
    with pytest.raises(HTTPException) as exc:
        client.get(f"/subjects/{test_model_subject.id}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_update_subject_unauthorized(client, test_model_subject):
    update_data = {"name": "Unauthorized Update"}
    with pytest.raises(HTTPException) as exc:
        client.put(f"/subjects/{test_model_subject.id}", json=update_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_delete_subject_unauthorized(client, test_model_subject):
    with pytest.raises(HTTPException) as exc:
        client.delete(f"/subjects/{test_model_subject.id}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_create_subject_duplicate_name(logged_in_client, test_model_discipline):
    subject_data = {"name": "Duplicate Subject", "discipline_ids": [test_model_discipline.id]}
    
    # Create the first subject
    response = logged_in_client.post("/subjects/", json=subject_data)
    assert response.status_code == 201

    # Try to create a subject with the same name
    response = logged_in_client.post("/subjects/", json=subject_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_update_subject_no_changes(logged_in_client, test_model_subject):
    update_data = {"name": test_model_subject.name}
    response = logged_in_client.put(f"/subjects/{test_model_subject.id}", json=update_data)
    logger.debug(response.json())
    assert response.status_code == 200
    assert response.json()["name"] == test_model_subject.name

def test_create_subject_long_name(logged_in_client, test_model_discipline):
    long_name = "A" * 101  # Assuming max length is 100
    subject_data = {"name": long_name, "discipline_ids": [test_model_discipline.id]}
    response = logged_in_client.post("/subjects/", json=subject_data)
    assert response.status_code == 422
    assert "String should have at most 100 characters" in response.json()["detail"][0]["msg"]

def test_update_subject_partial(logged_in_client, test_model_subject):
    update_data = {"name": "Partially Updated Subject"}
    response = logged_in_client.put(f"/subjects/{test_model_subject.id}", json=update_data)
    logger.debug(response.json())
    assert response.status_code == 200
    updated_subject = response.json()
    assert updated_subject["name"] == "Partially Updated Subject"
    assert len(updated_subject["disciplines"]) == len(test_model_subject.disciplines)

def test_create_subject_non_existent_discipline(logged_in_client):
    subject_data = {"name": "Invalid Subject Topic", "discipline_ids": [99999]}
    response = logged_in_client.post("/subjects/", json=subject_data)
    assert response.status_code == 400
    assert "Invalid discipline_id" in response.json()["detail"]

def test_update_subject_non_existent_discipline(logged_in_client, test_model_subject):
    update_data = {"name": "Invalid Subject Update", "discipline_ids": [99999]}
    response = logged_in_client.put(f"/subjects/{test_model_subject.id}", json=update_data)
    assert response.status_code == 404
    assert "Discipline not found" in response.json()["detail"]
