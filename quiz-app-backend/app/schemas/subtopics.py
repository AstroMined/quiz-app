# schemas/subtopics.py

from pydantic import BaseModel

class SubtopicBaseSchema(BaseModel):
    name: str

class SubtopicCreateSchema(SubtopicBaseSchema):
    pass

class SubtopicSchema(SubtopicBaseSchema):
    id: int

    class Config:
        from_attributes = True
