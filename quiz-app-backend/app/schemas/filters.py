# filename: app/schemas/filters.py

from typing import Optional, List
from pydantic import BaseModel, Field

class FilterParamsSchema(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = Field(None, description="List of tags")
