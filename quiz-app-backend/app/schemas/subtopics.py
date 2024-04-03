# schemas/subtopics.py

from pydantic import BaseModel

class SubtopicBase(BaseModel):
    name: str

class SubtopicCreate(SubtopicBase):
    pass

class Subtopic(SubtopicBase):
    id: int

    class Config:
        from_attributes = True