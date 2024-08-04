# filename: app/services/authentication_service.py

from sqlalchemy.orm import Session
from app.services.user_service import get_user_by_username
from app.core.security import verify_password, get_password_hash
from app.models.users import UserModel
from app.services.logging_service import logger


def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = get_user_by_username(db, username)
    if not user:
        logger.error(f"User {username} not found")
        return False
    logger.debug(f"Authenticating user: {username}")
    logger.debug(f"Stored hashed password: {user.hashed_password}")
    logger.debug(f"Provided password: {password}")
    
    # Add this line to log the result of verify_password
    verification_result = verify_password(password, user.hashed_password)
    logger.debug(f"Password verification result: {verification_result}")
    
    if not verification_result:
        hashed_attempt = get_password_hash(password)
        logger.debug(f"Hashed attempt: {hashed_attempt}")
        logger.error(f"User {username} supplied an invalid password")
        return False
    if not user.is_active:
        logger.error(f"User {username} is not active")
        return False
    logger.info(f"User {username} authenticated successfully")
    return user
