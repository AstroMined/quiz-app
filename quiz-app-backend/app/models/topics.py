# filename: app/models/topics.py
"""
This module defines the Topic model.

The Topic model represents a topic in the quiz app.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class TopicModel(Base):
    """
    The Topic model.

    Attributes:
        id (int): The primary key of the topic.
        name (str): The name of the topic.
        subject_id (int): The foreign key referencing the associated subject.
        subject (Subject): The relationship to the associated subject.
        subtopics (List[Subtopic]): The relationship to the associated subtopics.
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    subject = relationship("SubjectModel", back_populates="topics")
    subtopics = relationship("SubtopicModel", back_populates="topic")
