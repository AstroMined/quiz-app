# filename: app/schemas/user_responses.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UserResponseBaseSchema(BaseModel):
    user_id: int
    question_id: int
    answer_choice_id: int
    is_correct: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True

class UserResponseCreateSchema(UserResponseBaseSchema):
    timestamp: datetime = None

class UserResponseUpdateSchema(BaseModel):
    is_correct: Optional[bool] = None

class UserResponseSchema(UserResponseBaseSchema):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
