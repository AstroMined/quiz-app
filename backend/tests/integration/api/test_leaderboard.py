# filename: backend/tests/test_api/test_api_leaderboard.py

from backend.app.services.logging_service import logger


def test_get_user_leaderboard_empty(logged_in_client, test_model_user_with_group):
    user_id = test_model_user_with_group.id

    response = logged_in_client.get(f"/leaderboard/user/{user_id}")
    assert response.status_code == 200
    user_leaderboard = response.json()
    assert len(user_leaderboard) == 0


def test_get_group_leaderboard_empty(logged_in_client, test_model_user_with_group):
    group_id = test_model_user_with_group.groups[0].id

    response = logged_in_client.get(f"/leaderboard/group/{group_id}")
    assert response.status_code == 200
    group_leaderboard = response.json()
    assert len(group_leaderboard) == 0


def test_create_leaderboard_entry(
    logged_in_client, test_model_user_with_group, time_period_daily
):
    group_id = test_model_user_with_group.groups[0].id
    entry_data = {
        "user_id": test_model_user_with_group.id,
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": group_id,
    }

    response = logged_in_client.post("/leaderboard/", json=entry_data)
    logger.debug(response.json())
    assert response.status_code == 200
    created_entry = response.json()
    assert created_entry["user_id"] == test_model_user_with_group.id
    assert created_entry["score"] == 100
    assert created_entry["time_period_id"] == time_period_daily.id
    assert created_entry["group_id"] == group_id


def test_update_leaderboard_entry(
    logged_in_client, test_model_user_with_group, time_period_daily
):
    # First, create a leaderboard entry
    group_id = test_model_user_with_group.groups[0].id
    entry_data = {
        "user_id": test_model_user_with_group.id,
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": group_id,
    }
    create_response = logged_in_client.post("/leaderboard/", json=entry_data)
    logger.debug(create_response.json())
    created_entry = create_response.json()

    # Now, update the entry
    update_data = {"score": 150}
    update_response = logged_in_client.put(
        f"/leaderboard/{created_entry['id']}", json=update_data
    )
    logger.debug(update_response.json())
    assert update_response.status_code == 200
    updated_entry = update_response.json()
    assert updated_entry["id"] == created_entry["id"]
    assert updated_entry["score"] == 150


def test_delete_leaderboard_entry(
    logged_in_client, test_model_user_with_group, time_period_daily
):
    # First, create a leaderboard entry
    group_id = test_model_user_with_group.groups[0].id
    entry_data = {
        "user_id": test_model_user_with_group.id,
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": group_id,
    }
    create_response = logged_in_client.post("/leaderboard/", json=entry_data)
    logger.debug(create_response.json())
    created_entry = create_response.json()

    # Now, delete the entry
    delete_response = logged_in_client.delete(f"/leaderboard/{created_entry['id']}")
    logger.debug(f"Delete response status code: {delete_response.status_code}")
    assert delete_response.status_code == 204

    # Verify that the entry has been deleted
    get_response = logged_in_client.get(
        f"/leaderboard/user/{test_model_user_with_group.id}"
    )
    logger.debug(get_response.json())
    assert get_response.status_code == 200
    user_leaderboard = get_response.json()
    assert created_entry["id"] not in [entry["id"] for entry in user_leaderboard]


def test_get_leaderboard_with_limit(
    logged_in_client, setup_test_data, time_period_daily
):
    response = logged_in_client.get(
        f"/leaderboard/?time_period={time_period_daily.id}&limit=5"
    )
    logger.debug(response.json())
    assert response.status_code == 200
    leaderboard_data = response.json()
    assert len(leaderboard_data) == 5

    # Verify that the leaderboard is sorted by score in descending order
    scores = [entry["score"] for entry in leaderboard_data]
    assert scores == sorted(scores, reverse=True)


def test_create_leaderboard_entry_invalid_data(logged_in_client):
    invalid_entry_data = {
        "user_id": "invalid",
        "score": "not a number",
        "time_period_id": "invalid",
        "group_id": "invalid",
    }

    response = logged_in_client.post("/leaderboard/", json=invalid_entry_data)
    assert response.status_code == 422  # Unprocessable Entity


def test_update_leaderboard_entry_invalid_data(
    logged_in_client, test_model_user_with_group, time_period_daily
):
    # First, create a valid leaderboard entry
    group_id = test_model_user_with_group.groups[0].id
    entry_data = {
        "user_id": test_model_user_with_group.id,
        "score": 100,
        "time_period_id": time_period_daily.id,
        "group_id": group_id,
    }
    create_response = logged_in_client.post("/leaderboard/", json=entry_data)
    created_entry = create_response.json()

    # Now, try to update with invalid data
    invalid_update_data = {"score": "not a number"}
    update_response = logged_in_client.put(
        f"/leaderboard/{created_entry['id']}", json=invalid_update_data
    )
    assert update_response.status_code == 422  # Unprocessable Entity
