# filename: app/crud/crud_groups.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.groups import GroupModel
from app.schemas.groups import GroupCreateSchema, GroupUpdateSchema
from app.services.logging_service import logger

def create_group_crud(db: Session, group: GroupCreateSchema, creator_id: int):
    try:
        db_group = GroupModel(
            name=group.name,
            description=group.description,
            creator_id=creator_id
        )
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

def read_group_crud(db: Session, group_id: int):
    return db.query(GroupModel).filter(GroupModel.id == group_id).first()

def update_group_crud(db: Session, group_id: int, group: GroupUpdateSchema):
    db_group = read_group_crud(db, group_id)
    if db_group:
        try:
            update_data = group.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_group, key, value)
            db.commit()
            db.refresh(db_group)
            return db_group
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
    return None

def delete_group_crud(db: Session, group_id: int):
    db_group = read_group_crud(db, group_id)
    if db_group:
        group_dict = db_group.__dict__.copy()
        group_dict.pop('_sa_instance_state', None)
        print(f"Group: {group_dict}")
        db.delete(db_group)
        db.commit()
        return True
    return False
