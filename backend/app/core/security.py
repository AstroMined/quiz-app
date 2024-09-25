# filename: backend/app/core/security.py

from passlib.context import CryptContext
from pydantic import SecretStr

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    result = pwd_context.verify(plain_password, hashed_password)

    return result


def get_password_hash(password):
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    hashed = pwd_context.hash(password)

    return hashed
