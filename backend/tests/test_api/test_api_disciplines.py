# filepath: /backend/tests/test_api/test_api_disciplines.py

import pytest
from fastapi import HTTPException

def test_create_discipline(logged_in_client, test_model_domain, test_model_subject):
    discipline_data = {
        "name": "Test Discipline",
        "domain_ids": [test_model_domain.id],
        "subject_ids": [test_model_subject.id]
    }

    response = logged_in_client.post("/disciplines/", json=discipline_data)
    assert response.status_code == 201
    created_discipline = response.json()
    assert created_discipline["name"] == "Test Discipline"
    assert test_model_domain.id == created_discipline["domains"][0]["id"]
    assert test_model_subject.id == created_discipline["subjects"][0]["id"]

def test_get_disciplines(logged_in_client, test_model_discipline):
    response = logged_in_client.get("/disciplines/")
    assert response.status_code == 200
    disciplines = response.json()
    assert isinstance(disciplines, list)
    assert len(disciplines) == 1

def test_get_discipline(logged_in_client, test_model_discipline):
    response = logged_in_client.get(f"/disciplines/{test_model_discipline.id}")
    assert response.status_code == 200
    retrieved_discipline = response.json()
    assert retrieved_discipline["id"] == test_model_discipline.id
    assert retrieved_discipline["name"] == test_model_discipline.name

def test_update_discipline(logged_in_client, test_model_discipline):
    update_data = {"name": "Updated Discipline"}
    response = logged_in_client.put(f"/disciplines/{test_model_discipline.id}", json=update_data)
    assert response.status_code == 200
    updated_discipline = response.json()
    assert updated_discipline["name"] == "Updated Discipline"

def test_delete_discipline(logged_in_client, test_model_discipline):
    response = logged_in_client.delete(f"/disciplines/{test_model_discipline.id}")
    assert response.status_code == 204

    # Verify that the discipline has been deleted
    get_response = logged_in_client.get(f"/disciplines/{test_model_discipline.id}")
    assert get_response.status_code == 404

def test_create_discipline_unauthorized(client, test_model_domain):
    discipline_data = {
        "name": "Unauthorized Discipline",
        "domain_ids": [test_model_domain.id]
    }
    with pytest.raises(HTTPException) as exc:
        client.post("/disciplines/", json=discipline_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_disciplines_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/disciplines/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_nonexistent_discipline(logged_in_client):
    response = logged_in_client.get("/disciplines/99999")
    assert response.status_code == 404

def test_update_nonexistent_discipline(logged_in_client, test_model_domain):
    update_data = {
        "name": "Nonexistent Discipline",
        "domain_ids": [test_model_domain.id]
    }
    response = logged_in_client.put("/disciplines/99999", json=update_data)
    assert response.status_code == 404

def test_delete_nonexistent_discipline(logged_in_client):
    response = logged_in_client.delete("/disciplines/99999")
    assert response.status_code == 404