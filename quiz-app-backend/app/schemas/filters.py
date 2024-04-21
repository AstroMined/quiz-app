# filename: app/schemas/filters.py

from typing import Optional, List
from pydantic import BaseModel, Field

class FilterParamsSchema(BaseModel):
    subject: Optional[str] = Field(None, description="Filter questions by subject")
    topic: Optional[str] = Field(None, description="Filter questions by topic")
    subtopic: Optional[str] = Field(None, description="Filter questions by subtopic")
    difficulty: Optional[str] = Field(None, description="Filter questions by difficulty level")
    tags: Optional[List[str]] = Field(None, description="Filter questions by tags")

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Math",
                "topic": "Algebra",
                "subtopic": "Linear Equations",
                "difficulty": "Easy",
                "tags": ["equations", "solving"]
            }
        }
