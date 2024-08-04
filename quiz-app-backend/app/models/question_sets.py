# filename: app/models/question_sets.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class QuestionSetModel(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(String(1000))
    is_public = Column(Boolean, default=True, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("UserModel", back_populates="created_question_sets")
    questions = relationship("QuestionModel", secondary="question_set_to_question_association", back_populates="question_sets")
    groups = relationship("GroupModel", secondary="question_set_to_group_association", back_populates="question_sets")

    def __repr__(self):
        return f"<QuestionSetModel(id={self.id}, name='{self.name}', is_public={self.is_public}, creator_id={self.creator_id})>"
