# filename: app/schemas/question_sets.py

import re
from typing import List, Optional
from pydantic import BaseModel, validator


class QuestionSetBaseSchema(BaseModel):
    name: str
    is_public: bool = True
    question_ids: Optional[List[int]] = []
    creator_id: int = None
    group_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class QuestionSetCreateSchema(QuestionSetBaseSchema):
    name: str
    is_public: bool = True

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Question set name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Question set name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError(
                'Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces'
            )
        return name


class QuestionSetUpdateSchema(BaseModel):
    name: Optional[str] = None
    is_public: Optional[bool] = None
    question_ids: Optional[List[int]] = None
    group_ids: Optional[List[int]] = None

    class Config:
        arbitrary_types_allowed = True

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Question set name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Question set name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError(
                'Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces'
            )
        return name


class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    is_public: bool = True
    question_ids: Optional[List[int]] = []
    creator_id: int = None
    group_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True
