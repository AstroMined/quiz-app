# filename: app/schemas/question_sets.py

import re
from typing import List, Optional
from pydantic import BaseModel, validator

class QuestionSetBaseSchema(BaseModel):
    name: str

class QuestionSetCreateSchema(QuestionSetBaseSchema):
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

class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    is_public: bool = True
    question_ids: List[int] = []

    class Config:
        from_attributes = True
