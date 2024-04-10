# filename: app/schemas/question_tags.py

from typing import List, Optional
from pydantic import BaseModel

class QuestionTagBaseSchema(BaseModel):
    tag: str

class QuestionTagCreateSchema(QuestionTagBaseSchema):
    pass

class QuestionTagSchema(QuestionTagBaseSchema):
    id: int

    class Config:
        from_attributes = True
