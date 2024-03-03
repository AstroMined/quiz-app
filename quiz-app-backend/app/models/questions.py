# filename: app/models/questions.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'))
    
    subtopic = relationship("Subtopic", back_populates="questions")
    answer_choices = relationship("AnswerChoice", back_populates="question")
