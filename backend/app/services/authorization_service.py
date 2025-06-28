# filename: backend/app/services/authorization_service.py

from typing import List

from sqlalchemy.orm import Session

from backend.app.crud.crud_roles import (
    read_permissions_for_role_from_db,
    read_role_from_db,
)
from backend.app.models.groups import GroupModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def get_user_permissions(db: Session, user: UserModel) -> List[str]:
    # Use the role relationship or fetch by role_id if not loaded
    if user.role:
        role = user.role
    else:
        role = db.query(RoleModel).filter(RoleModel.id == user.role_id).first()
    
    if role:
        return [permission.name for permission in role.permissions]
    return []


def has_permission(db: Session, user: UserModel, required_permission: str) -> bool:
    # Use the read_role_by_name_from_db function to get the role
    user_role = read_role_from_db(db, user.role_id)

    if user_role:
        # Use the read_permissions_for_role_from_db function to get the permissions
        role_permissions = read_permissions_for_role_from_db(db, user_role.id)

        user_permissions = [permission.name for permission in role_permissions]
        has_perm = required_permission in user_permissions
        return has_perm
    return False


def is_group_owner(user: UserModel, group: GroupModel) -> bool:
    """
    Check if the user is the owner of the specified group.
    """
    return user.id == group.creator_id
