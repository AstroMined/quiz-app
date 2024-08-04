# filename: app/models/question_tags.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class QuestionTagModel(Base):
    __tablename__ = "question_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    questions = relationship("QuestionModel", secondary="question_to_tag_association", back_populates="question_tags")

    def __repr__(self):
        return f"<QuestionTagModel(id={self.id}, tag='{self.tag}')>"
