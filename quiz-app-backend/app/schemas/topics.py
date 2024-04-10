# filename: app/schemas/topics.py

from pydantic import BaseModel

class TopicBaseSchema(BaseModel):
    name: str
    subject_id: int

class TopicCreateSchema(TopicBaseSchema):
    pass

class TopicSchema(TopicBaseSchema):
    id: int

    class Config:
        from_attributes = True