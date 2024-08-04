# filename: app/models/answer_choices.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class AnswerChoiceModel(Base):
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(10000), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    explanation = Column(String(10000))

    questions = relationship("QuestionModel", secondary="question_to_answer_association", back_populates="answer_choices")
    user_responses = relationship("UserResponseModel", back_populates="answer_choice")

    def __repr__(self):
        return f"<AnswerChoiceModel(id={self.id}, text='{self.text[:50]}...', is_correct={self.is_correct})>"
