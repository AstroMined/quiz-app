# filename: app/schemas/permissions.py

import re
from typing import Optional
from pydantic import BaseModel, Field, validator

class PermissionBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the permission")
    description: Optional[str] = Field(None, max_length=200, description="Description of the permission")

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return v

class PermissionCreateSchema(PermissionBaseSchema):
    pass

class PermissionUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the permission")
    description: Optional[str] = Field(None, max_length=200, description="Description of the permission")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return v

class PermissionSchema(PermissionBaseSchema):
    id: int

    class Config:
        from_attributes = True
