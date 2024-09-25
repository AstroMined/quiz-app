# filename: backend/app/schemas/user.py

import re
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator

from backend.app.core.security import get_password_hash


class UserBaseSchema(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username of the user"
    )
    email: EmailStr = Field(..., description="Email address of the user")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[\w\-\.]+$", v):
            raise ValueError(
                "Username must contain only alphanumeric characters, hyphens, underscores, and periods"
            )
        return v


class UserCreateSchema(UserBaseSchema):
    password: SecretStr = Field(
        ..., min_length=8, max_length=100, description="Password for the user"
    )
    role_id: Optional[int] = Field(
        default=None, description="ID of the role for the user"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char in '!@#$%^&*(),.?":{}|<>' for char in password):
            raise ValueError("Password must contain at least one special character")
        return v

    def create_hashed_password(self):
        return get_password_hash(self.password.get_secret_value())


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username of the user"
    )
    email: Optional[EmailStr] = Field(None, description="Email address of the user")
    password: Optional[SecretStr] = Field(
        None, min_length=8, max_length=100, description="Password for the user"
    )
    role_id: Optional[int] = Field(None, description="ID of the role for the user")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v is not None and not re.match(r"^[\w\-\.]+$", v):
            raise ValueError(
                "Username must contain only alphanumeric characters, hyphens, underscores, and periods"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            return UserCreateSchema.validate_password(v)
        return v

    def create_hashed_password(self):
        if self.password:
            return get_password_hash(self.password.get_secret_value())
        return None


class UserSchema(UserBaseSchema):
    id: int
    is_active: bool
    is_admin: bool
    role: str
    groups: List[dict] = Field(default_factory=list)
    created_groups: List[dict] = Field(default_factory=list)
    created_question_sets: List[dict] = Field(default_factory=list)
    responses: List[dict] = Field(default_factory=list)
    leaderboards: List[dict] = Field(default_factory=list)

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v):
        if hasattr(v, "name"):
            return v.name
        return v

    @field_validator(
        "groups",
        "created_groups",
        "created_question_sets",
        "responses",
        "leaderboards",
        mode="before",
    )
    @classmethod
    def ensure_dict_list(cls, v):
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id} for item in v]

    class Config:
        from_attributes = True
