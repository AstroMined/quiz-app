# filename: app/schemas/concepts.py

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class ConceptBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the concept")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Concept name cannot be empty or whitespace')
        return v

class ConceptCreateSchema(ConceptBaseSchema):
    subtopic_ids: List[int] = Field(..., min_items=1, description="List of subtopic IDs associated with this concept")

    @field_validator('subtopic_ids')
    @classmethod
    def subtopic_ids_must_be_unique(cls, v: List[int]) -> List[int]:
        if len(set(v)) != len(v):
            raise ValueError('Subtopic IDs must be unique')
        return v

class ConceptUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the concept")
    subtopic_ids: Optional[List[int]] = Field(None, min_items=1, description="List of subtopic IDs associated with this concept")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Concept name cannot be empty or whitespace')
        return v

    @field_validator('subtopic_ids')
    @classmethod
    def subtopic_ids_must_be_unique(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None and len(set(v)) != len(v):
            raise ValueError('Subtopic IDs must be unique')
        return v

class ConceptSchema(ConceptBaseSchema):
    id: int
    subtopics: Optional[List[dict]] = Field(None, description="List of subtopics associated with this concept")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this concept")

    @field_validator('subtopics', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True
