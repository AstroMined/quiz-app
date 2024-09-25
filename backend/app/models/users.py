# filename: backend/app/models/users.py

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    token_blacklist_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("RoleModel", back_populates="users")
    responses = relationship(
        "UserResponseModel", back_populates="user", cascade="all, delete-orphan"
    )
    groups = relationship(
        "GroupModel", secondary="user_to_group_association", back_populates="users"
    )
    leaderboards = relationship(
        "LeaderboardModel", back_populates="user", cascade="all, delete-orphan"
    )
    created_groups = relationship(
        "GroupModel", back_populates="creator", cascade="all, delete-orphan"
    )
    created_question_sets = relationship(
        "QuestionSetModel", back_populates="creator", cascade="all, delete-orphan"
    )
    created_questions = relationship("QuestionModel", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role_id='{self.role_id}')>"
