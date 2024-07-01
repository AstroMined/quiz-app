# filename: app/models/groups.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import UserToGroupAssociation, QuestionSetToGroupAssociation


class GroupModel(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))

# Define relationships after all classes have been defined
GroupModel.users = relationship(
    "UserModel",
    secondary=UserToGroupAssociation.__tablename__,
    back_populates="groups"
)
GroupModel.creator = relationship("UserModel", back_populates="created_groups")
GroupModel.leaderboards = relationship("LeaderboardModel", back_populates="group")
GroupModel.question_sets = relationship(
    "QuestionSetModel",
    secondary=QuestionSetToGroupAssociation.__tablename__,
    back_populates="groups"
)
