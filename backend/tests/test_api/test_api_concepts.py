# filepath: /backend/tests/test_api/test_api_concepts.py

import pytest
from fastapi import HTTPException


def test_create_concept(logged_in_client, test_model_subtopic):
    concept_data = {"name": "Test Concept", "subtopic_ids": [test_model_subtopic.id]}

    response = logged_in_client.post("/concepts/", json=concept_data)
    assert response.status_code == 201
    created_concept = response.json()
    assert created_concept["name"] == "Test Concept"
    assert test_model_subtopic.id == created_concept["subtopics"][0]["id"]


def test_get_concepts(logged_in_client, test_model_concept):
    response = logged_in_client.get("/concepts/")
    assert response.status_code == 200
    concepts = response.json()
    assert isinstance(concepts, list)
    assert len(concepts) == 1


def test_get_concept(logged_in_client, test_model_concept):
    response = logged_in_client.get(f"/concepts/{test_model_concept.id}")
    assert response.status_code == 200
    retrieved_concept = response.json()
    assert retrieved_concept["id"] == test_model_concept.id
    assert retrieved_concept["name"] == test_model_concept.name


def test_update_concept(logged_in_client, test_model_concept, test_model_subtopic):
    update_data = {"name": "Updated Concept", "subtopic_ids": [test_model_subtopic.id]}

    response = logged_in_client.put(
        f"/concepts/{test_model_concept.id}", json=update_data
    )
    assert response.status_code == 200
    updated_concept = response.json()
    assert updated_concept["name"] == "Updated Concept"
    assert test_model_subtopic.id in [
        subtopic["id"] for subtopic in updated_concept["subtopics"]
    ]


def test_delete_concept(logged_in_client, test_model_concept):
    response = logged_in_client.delete(f"/concepts/{test_model_concept.id}")
    assert response.status_code == 204

    # Verify that the concept has been deleted
    get_response = logged_in_client.get(f"/concepts/{test_model_concept.id}")
    assert get_response.status_code == 404


def test_create_concept_unauthorized(client, test_model_subtopic):
    concept_data = {
        "name": "Unauthorized Concept",
        "subtopic_ids": [test_model_subtopic.id],
    }
    with pytest.raises(HTTPException) as exc:
        client.post("/concepts/", json=concept_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_concepts_unauthorized(client, test_model_concept):
    with pytest.raises(HTTPException) as exc:
        client.get("/concepts/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_nonexistent_concept(logged_in_client):
    response = logged_in_client.get("/concepts/99999")
    assert response.status_code == 404


def test_update_nonexistent_concept(logged_in_client, test_model_subtopic):
    update_data = {
        "name": "Nonexistent Concept",
        "subtopic_ids": [test_model_subtopic.id],
    }
    response = logged_in_client.put("/concepts/99999", json=update_data)
    assert response.status_code == 404


def test_delete_nonexistent_concept(logged_in_client):
    response = logged_in_client.delete("/concepts/99999")
    assert response.status_code == 404
