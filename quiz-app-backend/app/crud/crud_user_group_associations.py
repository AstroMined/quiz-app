# filename: app/crud/crud_user_group_associations.py

from sqlalchemy.orm import Session
from app.models.associations import UserToGroupAssociation
from app.models.users import UserModel
from app.models.groups import GroupModel

def add_user_to_group(db: Session, user_id: int, group_id: int):
    association = UserToGroupAssociation(user_id=user_id, group_id=group_id)
    db.add(association)
    db.commit()

def remove_user_from_group(db: Session, user_id: int, group_id: int):
    db.query(UserToGroupAssociation).filter_by(user_id=user_id, group_id=group_id).delete()
    db.commit()

def get_user_groups(db: Session, user_id: int):
    return db.query(GroupModel).join(UserToGroupAssociation).filter(UserToGroupAssociation.user_id == user_id).all()

def get_group_users(db: Session, group_id: int):
    return db.query(UserModel).join(UserToGroupAssociation).filter(UserToGroupAssociation.group_id == group_id).all()
