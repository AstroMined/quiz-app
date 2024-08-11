# filename: app/services/authorization_service.py

from typing import List

from sqlalchemy.orm import Session

from app.models.groups import GroupModel
from app.models.roles import RoleModel
from app.models.users import UserModel
from app.services.logging_service import logger


def get_user_permissions(db: Session, user: UserModel) -> List[str]:
    role = db.query(RoleModel).filter(RoleModel.name == user.role).first()
    if role:
        return [permission.name for permission in role.permissions]
    return []

def has_permission(db: Session, user: UserModel, required_permission: str) -> bool:
    logger.debug("Checking permission '%s' for user: %s", required_permission, user)
    user_role = db.query(RoleModel).filter(RoleModel.name == user.role).first()
    if user_role:
        user_permissions = [permission.name for permission in user_role.permissions]
        logger.debug("User permissions: %s", user_permissions)
        has_perm = required_permission in user_permissions
        logger.debug("User has permission '%s': %s", required_permission, has_perm)
        return has_perm
    logger.debug("User role not found")
    return False

def is_group_owner(user: UserModel, group: GroupModel) -> bool:
    """
    Check if the user is the owner of the specified group.
    """
    return user.id == group.creator_id

