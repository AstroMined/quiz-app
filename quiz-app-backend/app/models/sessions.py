# filename: app/models/sessions.py

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SessionQuestionModel(Base):
    __tablename__ = 'session_question'
    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    answered = Column(Boolean, default=False)
    correct = Column(Boolean, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    session = relationship("SessionModel", back_populates="questions")
    question = relationship("QuestionModel", back_populates="sessions")

class SessionQuestionSetModel(Base):
    __tablename__ = 'session_question_set'
    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    question_set_id = Column(Integer, ForeignKey('question_sets.id'), primary_key=True)
    question_limit = Column(Integer, nullable=True)  # Optional limit on questions from this set

    session = relationship("SessionModel", back_populates="question_sets")
    question_set = relationship("QuestionSetModel", back_populates="sessions")

class SessionModel(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    # Additional fields as needed, e.g., session name, date, etc.

    questions = relationship("SessionQuestionModel", back_populates="session")
    question_sets = relationship("SessionQuestionSetModel", back_populates="session")
