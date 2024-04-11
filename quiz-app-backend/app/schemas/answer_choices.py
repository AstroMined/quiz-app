# app/schemas/answer_choices.py
from pydantic import BaseModel

class AnswerChoiceBaseSchema(BaseModel):
    text: str
    is_correct: bool
    explanation: str

class AnswerChoiceCreateSchema(AnswerChoiceBaseSchema):
    pass

class AnswerChoiceSchema(BaseModel):
    id: int
    text: str
    is_correct: bool
    explanation: str

    class Config:
        from_attributes = True
