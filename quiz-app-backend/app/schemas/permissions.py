# filename: app/schemas/permissions.py

import re
from pydantic import BaseModel, validator


class PermissionBaseSchema(BaseModel):
    name: str
    description: str

class PermissionCreateSchema(PermissionBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return name

class PermissionUpdateSchema(BaseModel):
    name: str = None
    description: str = None

    @validator('name')
    def validate_name(cls, name):
        if name and not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return name

class PermissionSchema(PermissionBaseSchema):
    id: int

    class Config:
        from_attributes = True