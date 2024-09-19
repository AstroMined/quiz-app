# filepaths: backend/tests/test_api/test_api_question_tags.py

import pytest
from fastapi import HTTPException

from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.schemas.question_tags import QuestionTagCreateSchema

def test_create_question_tag(logged_in_client):
    tag_data = {
        "tag": "Test Tag"
    }

    response = logged_in_client.post("/question-tags/", json=tag_data)
    assert response.status_code == 201
    created_tag = response.json()
    assert created_tag["tag"] == "test tag"

def test_get_question_tags(logged_in_client, test_model_tag):
    response = logged_in_client.get("/question-tags/")
    assert response.status_code == 200
    tags = response.json()
    assert isinstance(tags, list)
    assert len(tags) > 0
    assert any(tag["id"] == test_model_tag.id for tag in tags)

def test_get_question_tag(logged_in_client, test_model_tag):
    response = logged_in_client.get(f"/question-tags/{test_model_tag.id}")
    assert response.status_code == 200
    retrieved_tag = response.json()
    assert retrieved_tag["id"] == test_model_tag.id
    assert retrieved_tag["tag"] == test_model_tag.tag.lower()

def test_update_question_tag(logged_in_client, test_model_tag):
    update_data = {
        "tag": "Updated Tag"
    }

    response = logged_in_client.put(f"/question-tags/{test_model_tag.id}", json=update_data)
    assert response.status_code == 200
    updated_tag = response.json()
    assert updated_tag["id"] == test_model_tag.id
    assert updated_tag["tag"] == "updated tag"

def test_delete_question_tag(logged_in_client, test_model_tag):
    response = logged_in_client.delete(f"/question-tags/{test_model_tag.id}")
    assert response.status_code == 204

    # Verify that the tag has been deleted
    get_response = logged_in_client.get(f"/question-tags/{test_model_tag.id}")
    assert get_response.status_code == 404

def test_create_question_tag_unauthorized(client):
    tag_data = {
        "tag": "Unauthorized Tag"
    }
    with pytest.raises(HTTPException) as exc:
        client.post("/question-tags/", json=tag_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_question_tags_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/question-tags/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_nonexistent_question_tag(logged_in_client):
    response = logged_in_client.get("/question-tags/99999")
    assert response.status_code == 404

def test_update_nonexistent_question_tag(logged_in_client):
    update_data = {
        "tag": "Nonexistent Tag"
    }
    response = logged_in_client.put("/question-tags/99999", json=update_data)
    assert response.status_code == 404

def test_delete_nonexistent_question_tag(logged_in_client):
    response = logged_in_client.delete("/question-tags/99999")
    assert response.status_code == 404

def test_create_duplicate_question_tag(logged_in_client):
    # First, create a new tag
    tag_data = {
        "tag": "Duplicate Test Tag"
    }
    response = logged_in_client.post("/question-tags/", json=tag_data)
    assert response.status_code == 201
    created_tag = response.json()
    assert created_tag["tag"] == "duplicate test tag"

    # Now, try to create the same tag again
    response = logged_in_client.post("/question-tags/", json=tag_data)
    assert response.status_code == 400
    assert "Tag already exists" in response.json()["detail"]

def test_get_question_tags_pagination(logged_in_client, db_session):
    # Create 15 tags
    for i in range(15):
        tag_data = QuestionTagCreateSchema(tag=f"Tag {i}")
        create_question_tag_in_db(db_session, tag_data.model_dump())

    # Test first page
    response = logged_in_client.get("/question-tags/?skip=0&limit=10")
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) == 10

    # Test second page
    response = logged_in_client.get("/question-tags/?skip=10&limit=10")
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) == 5  # Assuming there were no other tags in the database

def test_update_question_tag_no_changes(logged_in_client, test_model_tag):
    update_data = {
        "tag": test_model_tag.tag
    }
    response = logged_in_client.put(f"/question-tags/{test_model_tag.id}", json=update_data)
    assert response.status_code == 200
    updated_tag = response.json()
    assert updated_tag["id"] == test_model_tag.id
    assert updated_tag["tag"] == test_model_tag.tag.lower()