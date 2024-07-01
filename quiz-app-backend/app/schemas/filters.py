# filename: app/schemas/filters.py

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class FilterParamsSchema(BaseModel):
    subject: Optional[str] = Field(None, description="Filter questions by subject")
    topic: Optional[str] = Field(None, description="Filter questions by topic")
    subtopic: Optional[str] = Field(None, description="Filter questions by subtopic")
    difficulty: Optional[str] = Field(None, description="Filter questions by difficulty level")
    tags: Optional[List[str]] = Field(None, description="Filter questions by tags")

    @validator('difficulty')
    def validate_difficulty(cls, difficulty):
        valid_difficulties = ['Beginner', 'Easy', 'Medium', 'Hard', 'Expert']
        if difficulty and difficulty not in valid_difficulties:
            raise ValueError(f'Invalid difficulty. Must be one of: {", ".join(valid_difficulties)}')
        return difficulty

    class Config:
        extra = 'forbid'
        json_schema_extra = {
            "example": {
                "subject": "Math",
                "topic": "Algebra",
                "subtopic": "Linear Equations",
                "difficulty": "Easy",
                "tags": ["equations", "solving"]
            }
        }
