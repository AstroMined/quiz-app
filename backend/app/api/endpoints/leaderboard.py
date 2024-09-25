# filename: backend/app/api/endpoints/leaderboard.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import TimePeriod
from backend.app.crud.crud_groups import read_group_from_db
from backend.app.crud.crud_leaderboard import (
    create_leaderboard_entry_in_db,
    delete_leaderboard_entry_from_db,
    read_leaderboard_entries_for_group_from_db,
    read_leaderboard_entries_for_user_from_db,
    read_leaderboard_entries_from_db,
    read_or_create_time_period_in_db,
    update_leaderboard_entry_in_db,
)
from backend.app.crud.crud_user import read_user_from_db
from backend.app.db.session import get_db
from backend.app.schemas.leaderboard import (
    LeaderboardCreateSchema,
    LeaderboardSchema,
    LeaderboardUpdateSchema,
)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.services.logging_service import logger
from backend.app.services.scoring_service import (
    calculate_leaderboard_scores,
    time_period_to_schema,
)

router = APIRouter()


@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    request: Request,
    time_period: TimePeriod = Query(..., description="Time period for the leaderboard"),
    group_id: Optional[int] = None,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Retrieve leaderboard entries.

    This endpoint allows authenticated users to retrieve leaderboard entries for a specific time period and optionally for a specific group.

    Args:
        request (Request): The FastAPI request object.
        time_period (TimePeriod): The time period for the leaderboard (DAILY, WEEKLY, MONTHLY, YEARLY).
        group_id (Optional[int]): The ID of the group to filter leaderboard entries (if applicable).
        db (Session): The database session.
        limit (int): The maximum number of entries to return (default: 10, min: 1, max: 100).

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries.

    Raises:
        HTTPException: If the specified time period is invalid or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        time_period_model = read_or_create_time_period_in_db(db, time_period.value)
        if not time_period_model:
            raise HTTPException(status_code=400, detail="Invalid time period")

        leaderboard_scores = calculate_leaderboard_scores(
            db, time_period_model, group_id
        )

        for user_id, score in leaderboard_scores.items():
            entries = read_leaderboard_entries_from_db(
                db,
                time_period_id=time_period_model.id,
                user_id=user_id,
                group_id=group_id,
            )
            if entries:
                entry = entries[0]
                update_leaderboard_entry_in_db(db, entry.id, {"score": score})
            else:
                create_leaderboard_entry_in_db(
                    db,
                    {
                        "user_id": user_id,
                        "score": score,
                        "time_period_id": time_period_model.id,
                        "group_id": group_id,
                    },
                )

        leaderboard_entries = read_leaderboard_entries_from_db(
            db, time_period_id=time_period_model.id, group_id=group_id, limit=limit
        )

        return [
            LeaderboardSchema(
                id=entry.id,
                user_id=entry.user_id,
                score=entry.score,
                time_period_id=entry.time_period_id,
                time_period=time_period_to_schema(time_period_model),
                group_id=entry.group_id,
            )
            for entry in leaderboard_entries
        ]
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/leaderboard/user/{user_id}", response_model=List[LeaderboardSchema])
def get_user_leaderboard(
    request: Request,
    user_id: int = Path(
        ..., description="The ID of the user to get leaderboard entries for"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve leaderboard entries for a specific user.

    This endpoint allows authenticated users to retrieve all leaderboard entries for a specific user.

    Args:
        request (Request): The FastAPI request object.
        user_id (int): The ID of the user to retrieve leaderboard entries for.
        db (Session): The database session.

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries for the specified user.

    Raises:
        HTTPException: If the user is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        # Check if the user exists
        user = read_user_from_db(db, user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with ID {user_id} not found"
            )

        # Retrieve leaderboard entries for the user
        entries = read_leaderboard_entries_for_user_from_db(db, user_id)

        # Return an empty list if there are no leaderboard entries
        return [LeaderboardSchema.model_validate(entry) for entry in entries] or []
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/leaderboard/group/{group_id}", response_model=List[LeaderboardSchema])
def get_group_leaderboard(
    request: Request,
    group_id: int = Path(
        ..., description="The ID of the group to get leaderboard entries for"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve leaderboard entries for a specific group.

    Args:
        request (Request): The FastAPI request object.
        group_id (int): The ID of the group to retrieve leaderboard entries for.
        db (Session): The database session.

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries for the specified group.

    Raises:
        HTTPException: If the group is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        # Check if the group exists
        group = read_group_from_db(db, group_id)
        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group with ID {group_id} not found"
            )

        # Retrieve leaderboard entries for the group
        db_leaderboard_entries = read_leaderboard_entries_for_group_from_db(
            db, group_id
        )

        # Return an empty list if there are no leaderboard entries
        return [
            LeaderboardSchema.model_validate(entry) for entry in db_leaderboard_entries
        ] or []
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_group_leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/leaderboard/", response_model=LeaderboardSchema)
def post_leaderboard_entry(
    request: Request, entry: LeaderboardCreateSchema, db: Session = Depends(get_db)
):
    """
    Create a new leaderboard entry.

    This endpoint allows authenticated users to create a new leaderboard entry.

    Args:
        request (Request): The FastAPI request object.
        entry (LeaderboardCreateSchema): The leaderboard entry data to be created.
        db (Session): The database session.

    Returns:
        LeaderboardSchema: The created leaderboard entry.

    Raises:
        HTTPException: If the user is not authenticated or if there's an error creating the entry.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    logger.debug(f"Received leaderboard entry data: {entry.model_dump()}")

    try:
        created_entry = create_leaderboard_entry_in_db(db, entry.model_dump())
        logger.debug(f"Created leaderboard entry: {created_entry}")
        return LeaderboardSchema.model_validate(created_entry)
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error in post_leaderboard_entry: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error creating leaderboard entry: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in post_leaderboard_entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/leaderboard/{entry_id}", response_model=LeaderboardSchema)
def put_leaderboard_entry(
    request: Request,
    entry_id: int,
    entry: LeaderboardUpdateSchema,
    db: Session = Depends(get_db),
):
    """
    Update a specific leaderboard entry.

    This endpoint allows authenticated users to update an existing leaderboard entry.

    Args:
        request (Request): The FastAPI request object.
        entry_id (int): The ID of the leaderboard entry to update.
        entry (LeaderboardUpdateSchema): The updated leaderboard entry data.
        db (Session): The database session.

    Returns:
        LeaderboardSchema: The updated leaderboard entry.

    Raises:
        HTTPException: If the leaderboard entry with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        updated_entry = update_leaderboard_entry_in_db(db, entry_id, entry.model_dump())
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Leaderboard entry not found")
        return LeaderboardSchema.model_validate(updated_entry)
    except SQLAlchemyError as e:
        logger.error(f"Database error in put_leaderboard_entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating leaderboard entry")


@router.delete("/leaderboard/{entry_id}", status_code=204)
def delete_leaderboard_entry(
    request: Request, entry_id: int, db: Session = Depends(get_db)
):
    """
    Delete a specific leaderboard entry.

    This endpoint allows authenticated users to delete an existing leaderboard entry.

    Args:
        request (Request): The FastAPI request object.
        entry_id (int): The ID of the leaderboard entry to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the leaderboard entry with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        success = delete_leaderboard_entry_from_db(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Leaderboard entry not found")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_leaderboard_entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting leaderboard entry")
