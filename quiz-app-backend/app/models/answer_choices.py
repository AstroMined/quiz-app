# filename: app/models/answer_choices.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
class AnswerChoice(Base):
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_correct = Column(Boolean)
    question_id = Column(Integer, ForeignKey('questions.id'))
    
    question = relationship("Question", back_populates="answer_choices")
