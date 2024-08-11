# filename: app/schemas/question_sets.py

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class QuestionSetBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the question set")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the question set")
    is_public: bool = Field(True, description="Whether the question set is public or private")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class QuestionSetCreateSchema(QuestionSetBaseSchema):
    creator_id: int = Field(..., gt=0, description="ID of the user creating the question set")
    question_ids: List[int] = Field(default_factory=list, description="List of question IDs in the set")
    group_ids: List[int] = Field(default_factory=list, description="List of group IDs associated with the set")

class QuestionSetUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the question set")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the question set")
    is_public: Optional[bool] = Field(None, description="Whether the question set is public or private")
    question_ids: Optional[List[int]] = Field(None, description="List of question IDs in the set")
    group_ids: Optional[List[int]] = Field(None, description="List of group IDs associated with the set")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    creator_id: int
    questions: Optional[List[dict]] = Field(None, description="List of questions in the set")
    groups: Optional[List[dict]] = Field(None, description="List of groups associated with the set")

    @field_validator('questions', 'groups', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": getattr(item, 'name', None)} for item in v]

    class Config:
        from_attributes = True
