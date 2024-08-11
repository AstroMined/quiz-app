# filename: app/models/topics.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

    subjects = relationship("SubjectModel", secondary="subject_to_topic_association", back_populates="topics")
    subtopics = relationship("SubtopicModel", secondary="topic_to_subtopic_association", back_populates="topics")
    questions = relationship("QuestionModel", secondary="question_to_topic_association", back_populates="topics")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}')>"
