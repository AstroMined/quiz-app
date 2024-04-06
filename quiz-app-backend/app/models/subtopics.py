# filename: app/models/subtopics.py
"""
This module defines the Subtopic model.

The Subtopic model represents a subtopic in the quiz app.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SubtopicModel(Base):
    """
    The Subtopic model.

    Attributes:
        id (int): The primary key of the subtopic.
        name (str): The name of the subtopic.
        topic_id (int): The foreign key referencing the associated topic.
        topic (Topic): The relationship to the associated topic.
        questions (List[Question]): The relationship to the associated questions.
    """
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    topic_id = Column(Integer, ForeignKey('topics.id'))

    topic = relationship("TopicModel", back_populates="subtopics")
    questions = relationship("QuestionModel", back_populates="subtopic")
