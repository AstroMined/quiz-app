# filename: app/schemas/question_sets.py

from typing import List, Optional
from pydantic import BaseModel

class QuestionSetBaseSchema(BaseModel):
    name: str

class QuestionSetCreateSchema(QuestionSetBaseSchema):
    is_public: bool = True

class QuestionSetUpdateSchema(BaseModel):
    name: Optional[str] = None
    is_public: Optional[bool] = None
    question_ids: Optional[List[int]] = None

class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    is_public: bool = True
    question_ids: List[int] = []

    class Config:
        from_attributes = True
