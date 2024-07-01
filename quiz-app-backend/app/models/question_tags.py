# filename: app/models/question_tags.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import QuestionToTagAssociation


class QuestionTagModel(Base):
    __tablename__ = "question_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True)

    questions = relationship("QuestionModel", secondary=QuestionToTagAssociation.__table__, overlaps="tags")
