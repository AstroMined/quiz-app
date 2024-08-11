# filename: app/api/endpoints/groups.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.crud.crud_groups import (create_group_in_db, delete_group_from_db,
                                  read_group_from_db, update_group_in_db)
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.groups import (GroupCreateSchema, GroupSchema,
                                GroupUpdateSchema)
from app.services.logging_service import logger
from app.services.user_service import get_current_user

router = APIRouter()

@router.post("/groups", response_model=GroupSchema)
def create_group_endpoint(
    group_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Creating group with data: %s", group_data)
    try:
        logger.debug("Before calling create_group_in_db")
        group_data["db"] = db
        group_data["creator_id"] = current_user.id
        group = GroupCreateSchema(**group_data)
        created_group = create_group_in_db(db=db, group=group, creator_id=current_user.id)
        logger.debug("After calling create_group_in_db")
        logger.debug("Group created successfully: %s", created_group)
        logger.debug("Before returning the response")
        return created_group
    except ValidationError as e:
        logger.error("Validation error creating group: %s", e.errors())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"msg": err["msg"], "type": err["type"]} for err in e.errors()]
        ) from e
    except Exception as e:
        logger.exception("Error creating group: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e

@router.get("/groups/{group_id}", response_model=GroupSchema)
def get_group_endpoint(
    group_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

@router.put("/groups/{group_id}", response_model=GroupSchema)
def update_group_endpoint(
    group_id: int, 
    group_data: dict,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_from_db(db, group_id=group_id)
    logger.debug("db_group: %s", db_group)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can update the group")
    try:
        logger.debug("Updating group with data: %s", group_data)
        group = GroupUpdateSchema(**group_data)
        logger.debug("group: %s", group)
        updated_group = update_group_in_db(db=db, group_id=group_id, group=group)
        logger.debug("updated_group: %s", updated_group)
        return updated_group
    except ValidationError as e:
        logger.error("Validation error updating group: %s", e.errors())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"msg": err["msg"], "type": err["type"]} for err in e.errors()]
        ) from e
    except Exception as e:
        logger.exception("Error updating group: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e

@router.delete("/groups/{group_id}")
def delete_group_endpoint(
    group_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can delete the group")
    delete_group_from_db(db=db, group_id=group_id)
    return {"message": "Group deleted successfully"}
