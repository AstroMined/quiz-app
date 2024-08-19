# filename: backend/app/schemas/roles.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RoleBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Name of the role")
    description: Optional[str] = Field(None, max_length=200, description="Description of the role")
    default: bool = Field(False, description="Whether this is the default role for new users")

class RoleCreateSchema(RoleBaseSchema):
    permissions: List[str] = Field(..., min_items=1, description="List of permission names associated with the role")

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        return list(set(v))  # Remove duplicates

class RoleUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Name of the role")
    description: Optional[str] = Field(None, max_length=200, description="Description of the role")
    permissions: Optional[List[str]] = Field(None, min_items=1, description="List of permission names associated with the role")
    default: Optional[bool] = Field(None, description="Whether this is the default role for new users")

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        if v is not None:
            return list(set(v))  # Remove duplicates
        return v

class RoleSchema(RoleBaseSchema):
    id: int
    permissions: List[str] = Field(..., description="List of permission names associated with the role")

    @field_validator('permissions', mode='before')
    @classmethod
    def convert_permissions(cls, v):
        if isinstance(v, list) and all(isinstance(item, str) for item in v):
            return v
        elif isinstance(v, list) and all(hasattr(item, 'name') for item in v):
            return [item.name for item in v]
        else:
            raise ValueError("Permissions must be a list of strings or objects with 'name' attribute")

    class Config:
        from_attributes = True
