# filename: app/schemas/answer_choices.py

from pydantic import BaseModel, validator


class AnswerChoiceBaseSchema(BaseModel):
    text: str
    is_correct: bool
    explanation: str

class AnswerChoiceCreateSchema(AnswerChoiceBaseSchema):
    @validator('text')
    def validate_text(cls, text):
        if not text.strip():
            raise ValueError('Answer choice text cannot be empty or whitespace')
        if len(text) > 5000:
            raise ValueError('Answer choice text cannot exceed 5000 characters')
        return text

    @validator('explanation')
    def validate_explanation(cls, explanation):
        if len(explanation) > 10000:
            raise ValueError('Answer choice explanation cannot exceed 10000 characters')
        return explanation

class AnswerChoiceSchema(BaseModel):
    id: int
    text: str
    is_correct: bool
    explanation: str

    class Config:
        from_attributes = True
