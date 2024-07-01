# filename: app/schemas/topics.py

from pydantic import BaseModel, validator


class TopicBaseSchema(BaseModel):
    name: str
    subject_id: int

class TopicCreateSchema(TopicBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Topic name cannot exceed 100 characters')
        return name

class TopicSchema(TopicBaseSchema):
    id: int

    class Config:
        from_attributes = True
