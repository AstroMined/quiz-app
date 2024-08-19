# filename: backend/app/api/endpoints/groups.py

"""
Groups Management API

This module provides API endpoints for managing groups in the quiz application.
It includes operations for creating, reading, updating, and deleting groups.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_groups module.

Endpoints:
- POST /groups: Create a new group
- GET /groups/{group_id}: Retrieve a specific group by ID
- PUT /groups/{group_id}: Update a specific group
- DELETE /groups/{group_id}: Delete a specific group

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_groups import (create_group_in_db,
                                          delete_group_from_db,
                                          read_group_from_db,
                                          update_group_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.groups import (GroupCreateSchema, GroupSchema,
                                        GroupUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/groups", response_model=GroupSchema)
def post_group(
    group: GroupCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new group.

    This endpoint allows authenticated users to create a new group in the database.
    The group data is validated using the GroupCreateSchema.

    Args:
        group (GroupCreateSchema): The group data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        GroupSchema: The created group data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    validated_group = GroupCreateSchema(**group.model_dump())
    group_data = validated_group.model_dump()
    group_data["creator_id"] = current_user.id
    created_group = create_group_in_db(db=db, group_data=group_data)
    return GroupSchema.model_validate(created_group)

@router.get("/groups/{group_id}", response_model=GroupSchema)
def get_group(
    group_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific group by ID.

    This endpoint allows authenticated users to retrieve a single group by its ID.

    Args:
        group_id (int): The ID of the group to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        GroupSchema: The group data.

    Raises:
        HTTPException: If the group with the given ID is not found.
    """
    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupSchema.model_validate(db_group)

@router.put("/groups/{group_id}", response_model=GroupSchema)
def put_group(
    group_id: int, 
    group: GroupUpdateSchema,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific group.

    This endpoint allows authenticated users to update an existing group by its ID.
    Only the group creator can update the group.

    Args:
        group_id (int): The ID of the group to update.
        group (GroupUpdateSchema): The updated group data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        GroupSchema: The updated group data.

    Raises:
        HTTPException: 
            - 404: If the group with the given ID is not found.
            - 403: If the current user is not the creator of the group.
    """
    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can update the group")
    
    validated_group = GroupUpdateSchema(**group.model_dump())
    group_data = validated_group.model_dump()
    updated_group = update_group_in_db(db=db, group_id=group_id, group_data=group_data)
    return GroupSchema.model_validate(updated_group)

@router.delete("/groups/{group_id}", status_code=204)
def delete_group(
    group_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific group.

    This endpoint allows authenticated users to delete an existing group by its ID.
    Only the group creator can delete the group.

    Args:
        group_id (int): The ID of the group to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: 
            - 404: If the group with the given ID is not found.
            - 403: If the current user is not the creator of the group.
    """
    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can delete the group")
    delete_group_from_db(db=db, group_id=group_id)
    return None
