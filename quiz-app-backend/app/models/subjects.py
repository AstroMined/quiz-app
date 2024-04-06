# filename: app/models/subjects.py
"""
This module defines the Subject model.

The Subject model represents a subject in the quiz app.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SubjectModel(Base):
    """
    The Subject model.

    Attributes:
        id (int): The primary key of the subject.
        name (str): The name of the subject.
        topics (List[Topic]): The relationship to the associated topics.
    """
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    topics = relationship("TopicModel", back_populates="subject")
