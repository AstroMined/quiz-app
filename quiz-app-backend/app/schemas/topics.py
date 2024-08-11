# filename: app/schemas/topics.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TopicBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the topic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        return v

class TopicCreateSchema(TopicBaseSchema):
    subject_ids: List[int] = Field(..., min_items=1, description="List of subject IDs associated with this topic")
    subtopic_ids: Optional[List[int]] = Field(None, description="List of subtopic IDs associated with this topic")

class TopicUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the topic")
    subject_ids: Optional[List[int]] = Field(None, min_items=1, description="List of subject IDs associated with this topic")
    subtopic_ids: Optional[List[int]] = Field(None, description="List of subtopic IDs associated with this topic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        return v

class TopicSchema(TopicBaseSchema):
    id: int
    subjects: Optional[List[dict]] = Field(None, description="List of subjects associated with this topic")
    subtopics: Optional[List[dict]] = Field(None, description="List of subtopics associated with this topic")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this topic")

    @field_validator('subjects', 'subtopics', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True
