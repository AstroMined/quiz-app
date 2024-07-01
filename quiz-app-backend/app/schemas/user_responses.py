# filename: app/schemas/user_responses.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserResponseBaseSchema(BaseModel):
    user_id: int
    question_id: int
    answer_choice_id: int
    is_correct: Optional[bool] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponseCreateSchema(UserResponseBaseSchema):
    pass

class UserResponseUpdateSchema(UserResponseBaseSchema):
    answer_choice_id: Optional[int] = None

class UserResponseSchema(UserResponseBaseSchema):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt
        }
