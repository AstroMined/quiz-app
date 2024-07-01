# filename: app/schemas/groups.py

import re
from typing import Optional
from pydantic import BaseModel, validator
from app.services.logging_service import logger


class GroupBaseSchema(BaseModel):
    name: str
    creator_id: int
    description: Optional[str] = None

    class Config:
        from_attributes = True

class GroupCreateSchema(GroupBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Group name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Group name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return name

    @validator('description')
    def validate_description(cls, description):
        if description and len(description) > 500:
            raise ValueError('Group description cannot exceed 500 characters')
        return description

class GroupUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, name):
        if name == '':
            raise ValueError('Group name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Group name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return name

    @validator('description')
    def validate_description(cls, description):
        if description and len(description) > 500:
            raise ValueError('Group description cannot exceed 500 characters')
        return description

class GroupSchema(GroupBaseSchema):
    id: int
    creator_id: int
    description: Optional[str] = None

    class Config:
        from_attributes = True
