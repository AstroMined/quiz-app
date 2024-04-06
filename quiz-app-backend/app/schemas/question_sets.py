# filename: app/schemas/question_sets.py
"""
This module defines the Pydantic schemas for the QuestionSet model.

The schemas are used for input validation and serialization/deserialization of QuestionSet objects.
"""

from pydantic import BaseModel

class QuestionSetBaseSchema(BaseModel):
    """
    The base schema for a QuestionSet.

    Attributes:
        name (str): The name of the question set.
    """
    name: str

class QuestionSetCreateSchema(QuestionSetBaseSchema):
    """
    The schema for creating a QuestionSet.

    Inherits from QuestionSetBase.
    """
    pass

class QuestionSetUpdateSchema(QuestionSetBaseSchema):
    """
    The schema for updating a QuestionSet.

    Inherits from QuestionSetBase.
    """
    pass

class QuestionSetSchema(QuestionSetBaseSchema):
    """
    The schema representing a stored QuestionSet.

    Inherits from QuestionSetBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the question set.
    """
    id: int

    class Config:
        from_attributes = True
