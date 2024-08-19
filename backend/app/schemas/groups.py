# filename: backend/app/schemas/groups.py

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class GroupBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Description of the group")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class GroupCreateSchema(GroupBaseSchema):
    creator_id: int = Field(..., gt=0, description="ID of the user creating the group")

class GroupUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Description of the group")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class GroupSchema(GroupBaseSchema):
    id: int
    creator_id: int
    users: Optional[List[dict]] = Field(None, description="List of users in this group")
    question_sets: Optional[List[dict]] = Field(None, description="List of question sets associated with this group")

    @field_validator('users', 'question_sets', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": getattr(item, 'name', None)} for item in v]

    class Config:
        from_attributes = True
