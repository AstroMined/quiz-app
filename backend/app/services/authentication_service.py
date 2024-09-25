# filename: backend/app/services/authentication_service.py

from sqlalchemy.orm import Session

from backend.app.core.security import verify_password
from backend.app.crud.authentication import revoke_all_tokens_for_user
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.models.users import UserModel


def authenticate_user(db: Session, username: str, password: str = None) -> UserModel:
    user = read_user_by_username_from_db(db, username)

    if not user:
        return False

    if password is not None:
        verification_result = verify_password(password, user.hashed_password)
        if not verification_result:
            return False

    if not user.is_active:
        return False

    return user


def revoke_all_user_tokens(db: Session, user_id: int):
    """
    Revoke all tokens for a given user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose tokens should be revoked.

    Returns:
        None
    """
    revoke_all_tokens_for_user(db, user_id)
