# filename: app/schemas/user.py

import string
import re
from typing import Optional, List
from pydantic import BaseModel, validator, EmailStr, Field, model_validator
from app.schemas.groups import GroupSchema
from app.schemas.question_sets import QuestionSetSchema
from app.models.groups import GroupModel
from app.services.logging_service import logger


def validate_password(password: str) -> str:
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

def validate_username(username: str) -> str:
    if len(username) < 3:
        raise ValueError('Username must be at least 3 characters long')
    if len(username) > 50:
        raise ValueError('Username must not exceed 50 characters')
    if not re.match(r'^[\w\-\.]+$', username):
        raise ValueError('Username must contain only alphanumeric characters, hyphens, underscores, and periods')
    return username

def validate_email(email: str) -> str:
    if not email:
        raise ValueError('Email is required')
    return email

class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = Field(default='user')

    class Config:
        from_attributes = True

class UserCreateSchema(UserBaseSchema):
    password: str

    @validator('password')
    def validate_password(cls, password):
        return validate_password(password)

    @validator('username')
    def validate_username(cls, username):
        return validate_username(username)

    @validator('email')
    def validate_email(cls, email):
        return validate_email(email)

class UserUpdateSchema(UserBaseSchema):
    username: Optional[str] = None
    password: Optional[str] = None
    group_ids: Optional[List[int]] = None
    email: Optional[str] = None

    @validator('password')
    def validate_password(cls, password):
        return validate_password(password)

    @model_validator(mode='before')
    def validate_group_ids(cls, values):
        logger.debug("UserUpdateSchema received data: %s", values)
        if values.get('group_ids'):
            group_ids = values.get('group_ids')
            db = values.get('db')
            if not db:
                raise ValueError("Database session not provided")
            for group_id in group_ids:
                if not db.query(GroupModel).filter(GroupModel.id == group_id).first():
                    raise ValueError(f"Invalid group_id: {group_id}")
        return values

class UserSchema(UserBaseSchema):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    is_admin: bool
    group_ids: List[GroupSchema] = []
    created_groups: List[GroupSchema] = []
    created_question_sets: List[QuestionSetSchema] = []

    class Config:
        from_attributes = True