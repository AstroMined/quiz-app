# filename: app/schemas/user.py

import string
import re
from typing import Optional
from pydantic import BaseModel, validator, EmailStr


class UserBaseSchema(BaseModel):
    username: str


class UserCreateSchema(UserBaseSchema):
    password: str
    email: EmailStr

    @validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in password):
            raise ValueError(
                'Password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError(
                'Password must contain at least one lowercase letter')
        if not any(char in string.punctuation for char in password):
            raise ValueError(
                'Password must contain at least one special character')
        if any(char.isspace() for char in password):
            raise ValueError('Password must not contain whitespace characters')
        weak_passwords = [
            'password',
            '123456',
            'qwerty',
            'abc123',
            'letmein',
            'admin',
            'welcome',
            'monkey',
            '111111',
            'iloveyou'
        ]
        if password.lower() in weak_passwords:
            raise ValueError(
                'Password is too common. Please choose a stronger password.')
        return password

    @validator('username')
    def validate_username(cls, username):
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(username) > 50:
            raise ValueError('Username must not exceed 50 characters')
        # Regex to allow alphanumeric characters, hyphens, underscores, and periods
        if not re.match(r'^[\w\-\.]+$', username):
            raise ValueError(
                'Username must contain only alphanumeric characters, hyphens, underscores, and periods'
            )
        return username

    @validator('email')
    def validate_email(cls, email):
        if not email:
            raise ValueError('Email is required')
        return email


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserSchema(UserBaseSchema):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
