# filename: app/models/question_tags.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class QuestionTagModel(Base):
    __tablename__ = "question_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True)

    questions = relationship("QuestionModel", secondary="question_tag_association", overlaps="tags")

class QuestionTagAssociation(Base):
    __tablename__ = "question_tag_association"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("question_tags.id"), primary_key=True)
