# filename: app/models/answer_choices.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class AnswerChoiceModel(Base):
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_correct = Column(Boolean)
    explanation = Column(Text)  # Add the explanation field
    question_id = Column(Integer, ForeignKey('questions.id'))

    question = relationship("QuestionModel", back_populates="answer_choices")
