# filename: backend/app/models/subtopics.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class SubtopicModel(Base):
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

    topics = relationship(
        "TopicModel",
        secondary="topic_to_subtopic_association",
        back_populates="subtopics",
    )
    concepts = relationship(
        "ConceptModel",
        secondary="subtopic_to_concept_association",
        back_populates="subtopics",
    )
    questions = relationship(
        "QuestionModel",
        secondary="question_to_subtopic_association",
        back_populates="subtopics",
    )

    def __repr__(self):
        return f"<Subtopic(id={self.id}, name='{self.name}')>"
