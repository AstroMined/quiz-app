# filepath: /backend/tests/test_api/test_api_domains.py

import pytest
from fastapi import HTTPException


def test_create_domain(logged_in_client):
    domain_data = {"name": "Test Domain"}

    response = logged_in_client.post("/domains/", json=domain_data)
    assert response.status_code == 201
    created_domain = response.json()
    assert created_domain["name"] == "Test Domain"


def test_get_domains(logged_in_client, test_model_domain):
    response = logged_in_client.get("/domains/")
    assert response.status_code == 200
    domains = response.json()
    assert isinstance(domains, list)
    assert len(domains) == 1


def test_get_domain(logged_in_client, test_model_domain):
    response = logged_in_client.get(f"/domains/{test_model_domain.id}")
    assert response.status_code == 200
    retrieved_domain = response.json()
    assert retrieved_domain["id"] == test_model_domain.id
    assert retrieved_domain["name"] == test_model_domain.name


def test_update_domain(logged_in_client, test_model_domain):
    update_data = {"name": "Updated Domain"}

    response = logged_in_client.put(
        f"/domains/{test_model_domain.id}", json=update_data
    )
    assert response.status_code == 200
    updated_domain = response.json()
    assert updated_domain["name"] == "Updated Domain"


def test_delete_domain(logged_in_client, test_model_domain):
    response = logged_in_client.delete(f"/domains/{test_model_domain.id}")
    assert response.status_code == 204

    # Verify that the domain has been deleted
    get_response = logged_in_client.get(f"/domains/{test_model_domain.id}")
    assert get_response.status_code == 404


def test_create_domain_unauthorized(client):
    domain_data = {"name": "Unauthorized Domain"}
    with pytest.raises(HTTPException) as exc:
        client.post("/domains/", json=domain_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_domains_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/domains/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_nonexistent_domain(logged_in_client):
    response = logged_in_client.get("/domains/99999")
    assert response.status_code == 404


def test_update_nonexistent_domain(logged_in_client):
    update_data = {"name": "Nonexistent Domain"}
    response = logged_in_client.put("/domains/99999", json=update_data)
    assert response.status_code == 404


def test_delete_nonexistent_domain(logged_in_client):
    response = logged_in_client.delete("/domains/99999")
    assert response.status_code == 404
