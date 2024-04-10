# filename: app/models/question_sets.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.questions import question_set_question

class QuestionSetModel(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_public = Column(Boolean, default=True)

    questions = relationship("QuestionModel", secondary=question_set_question, back_populates="question_sets")
    sessions = relationship("SessionQuestionSetModel", back_populates="question_set")
