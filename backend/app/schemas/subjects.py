# filename: backend/app/schemas/subjects.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SubjectBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the subject")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        return v

class SubjectCreateSchema(SubjectBaseSchema):
    discipline_ids: List[int] = Field(..., min_items=1, description="List of discipline IDs associated with this subject")
    topic_ids: Optional[List[int]] = Field(None, description="List of topic IDs associated with this subject")

class SubjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the subject")
    discipline_ids: Optional[List[int]] = Field(None, min_items=1, description="List of discipline IDs associated with this subject")
    topic_ids: Optional[List[int]] = Field(None, description="List of topic IDs associated with this subject")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        return v

class SubjectSchema(SubjectBaseSchema):
    id: int
    disciplines: Optional[List[dict]] = Field(None, description="List of disciplines associated with this subject")
    topics: Optional[List[dict]] = Field(None, description="List of topics associated with this subject")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this subject")

    @field_validator('disciplines', 'topics', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True
