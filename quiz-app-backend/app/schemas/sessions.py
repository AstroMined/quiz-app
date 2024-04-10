# filename: app/schemas/tags.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SessionQuestionSchema(BaseModel):
    question_id: int
    answered: bool
    correct: Optional[bool] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class SessionQuestionSetSchema(BaseModel):
    question_set_id: int
    question_limit: Optional[int] = None  # Limit on questions from this set, if any

    class Config:
        from_attributes = True

class SessionBaseSchema(BaseModel):
    # Define basic session fields here. For simplicity, we'll just assume a name for the session.
    name: str = Field(..., description="The name of the session")

class SessionCreateSchema(SessionBaseSchema):
    # IDs of question sets to include in the session. Actual question selection/logic to be handled elsewhere.
    question_sets: List[int] = Field(default=[], description="List of question set IDs for the session")

class SessionUpdateSchema(SessionBaseSchema):
    # Assuming we might want to update the name or the question sets associated with the session.
    question_sets: Optional[List[int]] = Field(default=None, description="Optionally update the list of question set IDs for the session")

class SessionSchema(SessionBaseSchema):
    id: int
    question_sets: List[SessionQuestionSetSchema]
    questions: List[SessionQuestionSchema]
    # Assuming additional fields as necessary, for instance, session creation or modification dates.

    class Config:
        from_attributes = True

