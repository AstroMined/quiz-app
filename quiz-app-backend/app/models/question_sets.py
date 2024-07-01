# filename: app/models/question_sets.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, inspect, ARRAY
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import QuestionSetToQuestionAssociation, QuestionSetToGroupAssociation


class QuestionSetModel(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_public = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("UserModel", back_populates="created_question_sets")
    questions = relationship(
        "QuestionModel",
        secondary=QuestionSetToQuestionAssociation.__table__,
        back_populates="question_sets"
    )
    sessions = relationship("SessionQuestionSetModel", back_populates="question_set")
    groups = relationship(
        "GroupModel",
        secondary=QuestionSetToGroupAssociation.__table__,
        back_populates="question_sets"
    )

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
