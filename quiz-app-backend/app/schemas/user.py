# filename: app/schemas/user.py

import string
from typing import Optional
from pydantic import BaseModel, validator

class UserBaseSchema(BaseModel):
    username: str

class UserCreateSchema(UserBaseSchema):
    password: str

    @validator('password')
    def validate_password(cls, password):
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
