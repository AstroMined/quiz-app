# filename: app/models/topics.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    subject = relationship("SubjectModel", back_populates="topics")
    subtopics = relationship("SubtopicModel", back_populates="topic")
    questions = relationship("QuestionModel", back_populates="topic")