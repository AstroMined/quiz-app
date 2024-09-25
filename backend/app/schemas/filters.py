# filename: backend/app/schemas/filters.py

from typing import List, Optional

from pydantic import BaseModel, Field, validator

from backend.app.schemas.questions import DifficultyLevel


class FilterParamsSchema(BaseModel):
    subject: Optional[str] = Field(
        None, max_length=100, description="Filter questions by subject"
    )
    topic: Optional[str] = Field(
        None, max_length=100, description="Filter questions by topic"
    )
    subtopic: Optional[str] = Field(
        None, max_length=100, description="Filter questions by subtopic"
    )
    difficulty: Optional[DifficultyLevel] = Field(
        None, description="Filter questions by difficulty level"
    )
    question_tags: Optional[List[str]] = Field(
        None, max_items=10, description="Filter questions by tags"
    )

    @validator("question_tags")
    def validate_question_tags(cls, v):
        if v:
            return [tag.lower() for tag in v]
        return v

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "subject": "Math",
                "topic": "Algebra",
                "subtopic": "Linear Equations",
                "difficulty": "Easy",
                "question_tags": ["equations", "solving"],
            }
        }
