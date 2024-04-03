# app/schemas/answer_choices.py
from pydantic import BaseModel

class AnswerChoiceBase(BaseModel):
    """
    The base schema for an AnswerChoice.

    Attributes:
        text (str): The text of the answer choice.
        is_correct (bool): Indicates whether the answer choice is correct.
    """
    text: str
    is_correct: bool

class AnswerChoiceCreate(AnswerChoiceBase):
    """
    The schema for creating an AnswerChoice.

    Inherits from AnswerChoiceBase.
    """
    pass

class AnswerChoice(AnswerChoiceBase):
    """
    The schema representing a stored AnswerChoice.

    Inherits from AnswerChoiceBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the answer choice.
    """
    id: int

    class Config:
        from_attributes = True
