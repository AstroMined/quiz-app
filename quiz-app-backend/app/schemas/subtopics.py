# schemas/subtopics.py

from pydantic import BaseModel, validator

class SubtopicBaseSchema(BaseModel):
    name: str
    topic_id: int

class SubtopicCreateSchema(SubtopicBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Subtopic name cannot exceed 100 characters')
        return name

class SubtopicSchema(SubtopicBaseSchema):
    id: int

    class Config:
        from_attributes = True
