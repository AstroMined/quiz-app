# filename: app/models/questions.py

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from enum import Enum as PyEnum

class DifficultyLevel(PyEnum):
    BEGINNER = "Beginner"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(10000), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    subjects = relationship("SubjectModel", secondary="question_to_subject_association", back_populates="questions")
    topics = relationship("TopicModel", secondary="question_to_topic_association", back_populates="questions")
    subtopics = relationship("SubtopicModel", secondary="question_to_subtopic_association", back_populates="questions")
    concepts = relationship("ConceptModel", secondary="question_to_concept_association", back_populates="questions")
    question_tags = relationship("QuestionTagModel", secondary="question_to_tag_association", back_populates="questions")
    answer_choices = relationship("AnswerChoiceModel", secondary="question_to_answer_association", back_populates="questions")
    question_sets = relationship("QuestionSetModel", secondary="question_set_to_question_association", back_populates="questions")
    user_responses = relationship("UserResponseModel", back_populates="question", cascade="all, delete-orphan")
    creator = relationship("UserModel", back_populates="created_questions")

    def __repr__(self):
        return f"<QuestionModel(id={self.id}, text='{self.text[:50]}...', difficulty='{self.difficulty}')>"
