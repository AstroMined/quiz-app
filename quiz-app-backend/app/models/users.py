# filename: app/models/users.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import UserToGroupAssociation


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String)

# Define relationships after all classes have been defined
UserModel.responses = relationship("UserResponseModel", back_populates="user")
UserModel.groups = relationship(
    "GroupModel",
    secondary=UserToGroupAssociation.__table__,
    back_populates="users"
)
UserModel.leaderboards = relationship("LeaderboardModel", back_populates="user")
UserModel.created_groups = relationship("GroupModel", back_populates="creator")
UserModel.created_question_sets = relationship("QuestionSetModel", back_populates="creator")
