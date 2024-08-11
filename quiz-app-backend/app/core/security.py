# filename: app/core/security.py

from passlib.context import CryptContext
from pydantic import SecretStr

from app.services.logging_service import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    result = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"verify_password called with plain_password: {plain_password}, hashed_password: {hashed_password}")
    logger.debug(f"verify_password result: {result}")
    return result

def get_password_hash(password):
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    hashed = pwd_context.hash(password)
    logger.debug(f"get_password_hash called with password: {password}")
    logger.debug(f"get_password_hash result: {hashed}")
    return hashed
