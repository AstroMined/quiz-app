# filename: backend/app/models/concepts.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class ConceptModel(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

    subtopics = relationship(
        "SubtopicModel",
        secondary="subtopic_to_concept_association",
        back_populates="concepts",
    )
    questions = relationship(
        "QuestionModel",
        secondary="question_to_concept_association",
        back_populates="concepts",
    )

    def __repr__(self):
        return f"<Concept(id={self.id}, name='{self.name}')>"
