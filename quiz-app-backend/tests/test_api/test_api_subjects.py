# filename: tests/test_api_subjects.py

from app.schemas.subjects import SubjectCreateSchema


def test_create_subject(logged_in_client, db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    response = logged_in_client.post("/subjects/", json=subject_data.dict())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Subject"

def test_read_subject(logged_in_client, db_session):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = logged_in_client.post("/subjects/", json=subject_data.dict()).json()

    # Read the created subject
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Subject"

def test_update_subject(logged_in_client, db_session):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = logged_in_client.post("/subjects/", json=subject_data.dict()).json()

    # Update the subject
    updated_data = {"name": "Updated Subject"}
    response = logged_in_client.put(f"/subjects/{created_subject['id']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Subject"

def test_delete_subject(logged_in_client, db_session):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = logged_in_client.post("/subjects/", json=subject_data.dict()).json()

    # Delete the subject
    response = logged_in_client.delete(f"/subjects/{created_subject['id']}")
    assert response.status_code == 204

    # Check if the subject was deleted
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 404