# filename: backend/app/api/endpoints/leaderboard.py

"""
Leaderboard Management API

This module provides API endpoints for managing leaderboards in the quiz application.
It includes operations for retrieving, creating, updating, and deleting leaderboard entries.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_leaderboard module.

Endpoints:
- GET /leaderboard/: Retrieve leaderboard entries
- GET /leaderboard/user/{user_id}: Retrieve leaderboard entries for a specific user
- GET /leaderboard/group/{group_id}: Retrieve leaderboard entries for a specific group
- POST /leaderboard/: Create a new leaderboard entry
- PUT /leaderboard/{entry_id}: Update a specific leaderboard entry
- DELETE /leaderboard/{entry_id}: Delete a specific leaderboard entry

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.app.crud.crud_leaderboard import (
    create_leaderboard_entry_in_db, delete_leaderboard_entry_from_db,
    read_leaderboard_entries_for_group_from_db,
    read_leaderboard_entries_for_user_from_db,
    read_leaderboard_entries_from_db,
    read_or_create_time_period_in_db, update_leaderboard_entry_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.leaderboard import (LeaderboardCreateSchema,
                                             LeaderboardSchema,
                                             LeaderboardUpdateSchema)
from backend.app.services.scoring_service import (calculate_leaderboard_scores,
                                                  time_period_to_schema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    time_period: int = Query(..., description="Time period ID (1: daily, 7: weekly, 30: monthly, 365: yearly)"),
    group_id: Optional[int] = None,
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve leaderboard entries.

    This endpoint allows authenticated users to retrieve leaderboard entries for a specific time period and optionally for a specific group.

    Args:
        time_period (int): The time period ID for the leaderboard (1: daily, 7: weekly, 30: monthly, 365: yearly).
        group_id (Optional[int]): The ID of the group to filter leaderboard entries (if applicable).
        db (Session): The database session.
        limit (int): The maximum number of entries to return (default: 10).
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries.

    Raises:
        HTTPException: If the specified time period is invalid.
    """
    time_period_model = read_or_create_time_period_in_db(db, {"id": time_period})
    if not time_period_model:
        raise HTTPException(status_code=400, detail="Invalid time period")

    leaderboard_scores = calculate_leaderboard_scores(db, time_period_model, group_id)
    
    for user_id, score in leaderboard_scores.items():
        entries = read_leaderboard_entries_from_db(db, time_period_id=time_period_model.id, user_id=user_id, group_id=group_id)
        if entries:
            entry = entries[0]
            update_leaderboard_entry_in_db(db, entry.id, {"score": score})
        else:
            create_leaderboard_entry_in_db(db, {
                "user_id": user_id,
                "score": score,
                "time_period_id": time_period_model.id,
                "group_id": group_id
            })

    leaderboard_entries = read_leaderboard_entries_from_db(
        db, time_period_id=time_period_model.id, group_id=group_id, limit=limit
    )

    return [
        LeaderboardSchema(
            id=entry.id,
            user_id=entry.user_id,
            score=entry.score,
            time_period=time_period_to_schema(time_period_model),
            group_id=entry.group_id
        )
        for entry in leaderboard_entries
    ]

@router.get("/leaderboard/user/{user_id}", response_model=List[LeaderboardSchema])
def get_user_leaderboard(
    user_id: int = Path(..., description="The ID of the user to get leaderboard entries for"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve leaderboard entries for a specific user.

    This endpoint allows authenticated users to retrieve all leaderboard entries for a specific user.

    Args:
        user_id (int): The ID of the user to retrieve leaderboard entries for.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries for the specified user.
    """
    entries = read_leaderboard_entries_for_user_from_db(db, user_id)
    return [LeaderboardSchema.model_validate(entry) for entry in entries]

@router.get("/leaderboard/group/{group_id}", response_model=List[LeaderboardSchema])
def get_group_leaderboard(
    group_id: int = Path(..., description="The ID of the group to get leaderboard entries for"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve leaderboard entries for a specific group.

    This endpoint allows authenticated users to retrieve all leaderboard entries for a specific group.

    Args:
        group_id (int): The ID of the group to retrieve leaderboard entries for.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries for the specified group.
    """
    entries = read_leaderboard_entries_for_group_from_db(db, group_id)
    return [LeaderboardSchema.model_validate(entry) for entry in entries]

@router.post("/leaderboard/", response_model=LeaderboardSchema)
def post_leaderboard_entry(
    entry: LeaderboardCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new leaderboard entry.

    This endpoint allows authenticated users to create a new leaderboard entry.

    Args:
        entry (LeaderboardCreateSchema): The leaderboard entry data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        LeaderboardSchema: The created leaderboard entry.
    """
    return create_leaderboard_entry_in_db(db, entry.model_dump())

@router.put("/leaderboard/{entry_id}", response_model=LeaderboardSchema)
def put_leaderboard_entry(
    entry_id: int,
    entry: LeaderboardUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific leaderboard entry.

    This endpoint allows authenticated users to update an existing leaderboard entry.

    Args:
        entry_id (int): The ID of the leaderboard entry to update.
        entry (LeaderboardUpdateSchema): The updated leaderboard entry data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        LeaderboardSchema: The updated leaderboard entry.

    Raises:
        HTTPException: If the leaderboard entry with the given ID is not found.
    """
    updated_entry = update_leaderboard_entry_in_db(db, entry_id, entry.model_dump())
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Leaderboard entry not found")
    return LeaderboardSchema.model_validate(updated_entry)

@router.delete("/leaderboard/{entry_id}", status_code=204)
def delete_leaderboard_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific leaderboard entry.

    This endpoint allows authenticated users to delete an existing leaderboard entry.

    Args:
        entry_id (int): The ID of the leaderboard entry to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: If the leaderboard entry with the given ID is not found.
    """
    success = delete_leaderboard_entry_from_db(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Leaderboard entry not found")
    return None
