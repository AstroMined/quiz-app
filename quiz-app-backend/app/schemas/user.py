# filename: app/schemas/user.py
"""
This module defines the Pydantic schemas for the User model.

The schemas are used for input validation and serialization/deserialization of User objects.
"""

from pydantic import BaseModel, validator

class UserBase(BaseModel):
    """
    The base schema for a User.

    Attributes:
        username (str): The username of the user.
    """
    username: str

class UserCreate(UserBase):
    """
    The schema for creating a User.

    Inherits from UserBase and includes additional attributes required for user creation.

    Attributes:
        password (str): The password of the user.
    """
    password: str

    @validator('password')
    def password_validation(cls, v):
        """
        Validate the password.

        The password must be at least 8 characters long.
        Additional validation rules can be added as needed.

        Args:
            v (str): The password value.

        Returns:
            str: The validated password.

        Raises:
            ValueError: If the password is invalid.
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

class UserLogin(BaseModel):
    """
    The schema for user login.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
    """
    username: str
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True