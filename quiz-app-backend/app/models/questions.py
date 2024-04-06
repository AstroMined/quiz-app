# filename: app/models/questions.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'))
    question_set_id = Column(Integer, ForeignKey('question_sets.id'))
    explanation = Column(String)  # Add this line
    
    subtopic = relationship("SubtopicModel", back_populates="questions")
    question_set = relationship("QuestionSetModel", back_populates="questions")
    answer_choices = relationship("AnswerChoiceModel", back_populates="question", cascade="all, delete-orphan")
