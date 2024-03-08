# filename: app/models/questions.py
"""
This module defines the Question model.

The Question model represents a question in the quiz app.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Question(Base):
    """
    The Question model.

    Attributes:
        id (int): The primary key of the question.
        text (str): The text of the question.
        subtopic_id (int): The foreign key referencing the associated subtopic.
        subtopic (Subtopic): The relationship to the associated subtopic.
        answer_choices (List[AnswerChoice]): The relationship to the associated answer choices.
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'))
    
    subtopic = relationship("Subtopic", back_populates="questions")
    answer_choices = relationship("AnswerChoice", back_populates="question")