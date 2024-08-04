# filename: app/schemas/question_tags.py

from typing import Optional
from pydantic import BaseModel, Field, validator

class QuestionTagBaseSchema(BaseModel):
    tag: str = Field(..., min_length=1, max_length=50)

    @validator('tag')
    def validate_tag(cls, v):
        if not v.strip():
            raise ValueError('Tag cannot be empty or only whitespace')
        return v.lower()  # Store tags in lowercase for consistency

class QuestionTagCreateSchema(QuestionTagBaseSchema):
    pass

class QuestionTagUpdateSchema(BaseModel):
    tag: Optional[str] = Field(None, min_length=1, max_length=50)

    @validator('tag')
    def validate_tag(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Tag cannot be empty or only whitespace')
            return v.lower()
        return v

class QuestionTagSchema(QuestionTagBaseSchema):
    id: int

    class Config:
        from_attributes = True
