# filename: app/models/groups.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class GroupModel(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("UserModel", secondary="user_to_group_association", back_populates="groups")
    creator = relationship("UserModel", back_populates="created_groups", foreign_keys=[creator_id])
    leaderboards = relationship("LeaderboardModel", back_populates="group", cascade="all, delete-orphan")
    question_sets = relationship("QuestionSetModel", secondary="question_set_to_group_association", back_populates="groups")

    def __repr__(self):
        return f"<GroupModel(id={self.id}, name='{self.name}', creator_id={self.creator_id}, is_active={self.is_active})>"
