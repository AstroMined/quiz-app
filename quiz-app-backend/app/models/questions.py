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
    """
    __tablename__ = "questions"
    def __repr__(self):
        return f"<Question(id={self.id}, text={self.text}, subtopic_id={self.subtopic_id}, question_set_id={self.question_set_id})>"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'))
    question_set_id = Column(Integer, ForeignKey('question_sets.id'))
    explanation = Column(String)  # Add this line
    
    subtopic = relationship("Subtopic", back_populates="questions")
    question_set = relationship("QuestionSet", back_populates="questions")
    answer_choices = relationship("AnswerChoice", back_populates="question")
