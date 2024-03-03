# filename: app/models/subtopics.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
class Subtopic(Base):
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    
    topic = relationship("Topic", back_populates="subtopics")
    questions = relationship("Question", back_populates="subtopic")
