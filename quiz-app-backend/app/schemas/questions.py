# filename: app/schemas/questions.py
"""
This module defines the Pydantic schemas for the Question model.

The schemas are used for input validation and serialization/deserialization of Question objects.
"""

from pydantic import BaseModel

class QuestionBase(BaseModel):
    """
    The base schema for a Question.

    Attributes:
        text (str): The text of the question.
    """
    text: str

class QuestionCreate(QuestionBase):
    """
    The schema for creating a Question.

    Inherits from QuestionBase.
    """
    pass

class QuestionUpdate(QuestionBase):
    """
    The schema for updating a Question.

    Inherits from QuestionBase.
    """
    pass

class Question(QuestionBase):
    """
    The schema representing a stored Question.

    Inherits from QuestionBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the question.
        subtopic_id (int): The ID of the associated subtopic.
        question_set_id (int): The ID of the associated question set.
    """
    id: int
    subtopic_id: int
    question_set_id: int

    class Config:
        from_attributes = True