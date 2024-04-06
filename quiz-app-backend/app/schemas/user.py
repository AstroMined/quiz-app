# filename: app/schemas/user.py
"""
This module defines the Pydantic schemas for the User model.
"""

import string
from pydantic import BaseModel, validator

class UserBaseSchema(BaseModel):
    """
    The base schema for a User.
    """
    username: str

class UserCreateSchema(UserBaseSchema):
    """
    The schema for creating a User.
    """
    password: str

    @validator('password')
    def validate_password(cls, password):
        """
        Validate the password.

        The password must be at least 8 characters long and contain at least one digit,
        one uppercase letter, one lowercase letter, and one special character.
        """
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char in string.punctuation for char in password):
            raise ValueError('Password must contain at least one special character')
        if any(char.isspace() for char in password):
            raise ValueError('Password must not contain whitespace characters')
        weak_passwords = ['password', '123456', 'qwerty', 'abc123', 'letmein', 'admin', 'welcome', 'monkey', '111111', 'iloveyou']
        if password.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password.')
        return password

class UserLoginSchema(BaseModel):
    """
    The schema for user login.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
    """
    username: str
    password: str

class UserSchema(UserBaseSchema):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True
