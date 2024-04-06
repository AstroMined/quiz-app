# filename: app/models/answer_choices.py
"""
This module defines the AnswerChoice model.

The AnswerChoice model represents an answer choice for a question in the quiz app.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class AnswerChoiceModel(Base):
    """
    The AnswerChoice model.

    Attributes:
        id (int): The primary key of the answer choice.
        text (str): The text of the answer choice.
        is_correct (bool): Indicates whether the answer choice is correct.
        question_id (int): The foreign key referencing the associated question.
        question (Question): The relationship to the associated question.
    """
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_correct = Column(Boolean)
    question_id = Column(Integer, ForeignKey('questions.id'))
    
    question = relationship("QuestionModel", back_populates="answer_choices")
