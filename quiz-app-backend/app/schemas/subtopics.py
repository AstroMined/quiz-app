# filename: app/schemas/subtopics.py

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class SubtopicBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the subtopic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        return v

class SubtopicCreateSchema(SubtopicBaseSchema):
    topic_ids: List[int] = Field(..., min_items=1, description="List of topic IDs associated with this subtopic")
    concept_ids: Optional[List[int]] = Field(None, description="List of concept IDs associated with this subtopic")

class SubtopicUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the subtopic")
    topic_ids: Optional[List[int]] = Field(None, min_items=1, description="List of topic IDs associated with this subtopic")
    concept_ids: Optional[List[int]] = Field(None, description="List of concept IDs associated with this subtopic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        return v

class SubtopicSchema(SubtopicBaseSchema):
    id: int
    topics: Optional[List[dict]] = Field(None, description="List of topics associated with this subtopic")
    concepts: Optional[List[dict]] = Field(None, description="List of concepts associated with this subtopic")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this subtopic")

    @field_validator('topics', 'concepts', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True
