# filename: backend/app/schemas/answer_choices.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, validator


class AnswerChoiceBaseSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    is_correct: bool
    explanation: Optional[str] = Field(None, max_length=10000)

    @validator("text", "explanation")
    def validate_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty or only whitespace")
        return v


class AnswerChoiceCreateSchema(AnswerChoiceBaseSchema):
    question_ids: Optional[list[int]] = None


class AnswerChoiceUpdateSchema(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=10000)
    is_correct: Optional[bool] = None
    explanation: Optional[str] = Field(None, max_length=10000)

    @validator("text", "explanation")
    def validate_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty or only whitespace")
        return v


class AnswerChoiceSchema(AnswerChoiceBaseSchema):
    id: int

    class Config:
        from_attributes = True


class DetailedAnswerChoiceSchema(BaseModel):
    id: int
    text: str = Field(
        ..., min_length=1, max_length=10000, description="The text of the question"
    )
    is_correct: bool = Field(..., description="Whether this answer choice is correct")
    explanation: Optional[str] = Field(
        None, max_length=10000, description="Explanation for this answer choice"
    )
    questions: List[dict] = Field(
        ..., description="List of questions associated with this answer choice"
    )

    @field_validator("questions", mode="before")
    @classmethod
    def ensure_dict_list(cls, v):
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        elif isinstance(v, list) and all(isinstance(item, str) for item in v):
            return [{"name": item} for item in v]
        elif isinstance(v, list) and all(hasattr(item, "text") for item in v):
            return [{"id": item.id, "name": item.text} for item in v]
        else:
            raise ValueError(
                "Must be a list of dictionaries, strings, or objects with 'text' attribute"
            )

    class Config:
        from_attributes = True
