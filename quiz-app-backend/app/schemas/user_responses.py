# filename: app/schemas/user_responses.py
"""
This module defines the Pydantic schemas for the UserResponse model.

The schemas are used for input validation and serialization/deserialization of UserResponse objects.
"""

from datetime import datetime
from pydantic import BaseModel

class UserResponseBaseSchema(BaseModel):
    """
    The base schema for a UserResponse.

    Attributes:
        user_id (int): The ID of the user.
        question_id (int): The ID of the question.
        answer_choice_id (int): The ID of the answer choice.
        is_correct (bool): Indicates whether the user's response is correct.
    """
    user_id: int
    question_id: int
    answer_choice_id: int
    is_correct: bool

class UserResponseCreateSchema(UserResponseBaseSchema):
    """
    The schema for creating a UserResponse.

    Inherits from UserResponseBase.
    """
    pass

class UserResponseSchema(UserResponseBaseSchema):
    """
    The schema representing a stored UserResponse.

    Inherits from UserResponseBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the user response.
        timestamp (datetime): The timestamp of the user's response.
    """
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
