# filename: app/models/question_sets.py
"""
This module defines the QuestionSet model.

The QuestionSet model represents a set of questions in the quiz app.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class QuestionSet(Base):
    """
    The QuestionSet model.

    Attributes:
        id (int): The primary key of the question set.
        name (str): The name of the question set.
        questions (List[Question]): The relationship to the associated questions.
    """
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    questions = relationship("Question", back_populates="question_set")