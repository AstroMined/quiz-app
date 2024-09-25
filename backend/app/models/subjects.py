# filename: backend/app/models/subjects.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class SubjectModel(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    disciplines = relationship(
        "DisciplineModel",
        secondary="discipline_to_subject_association",
        back_populates="subjects",
    )
    topics = relationship(
        "TopicModel",
        secondary="subject_to_topic_association",
        back_populates="subjects",
    )
    questions = relationship(
        "QuestionModel",
        secondary="question_to_subject_association",
        back_populates="subjects",
    )

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}')>"
