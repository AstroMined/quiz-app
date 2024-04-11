# filename: app/models/questions.py

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect
from app.db.base_class import Base

question_set_question = Table('question_set_question', Base.metadata,
    Column('question_id', ForeignKey('questions.id'), primary_key=True),
    Column('question_set_id', ForeignKey('question_sets.id'), primary_key=True)
)

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"))
    difficulty = Column(String)

    subject = relationship("SubjectModel", back_populates="questions")
    topic = relationship("TopicModel", back_populates="questions")
    subtopic = relationship("SubtopicModel", back_populates="questions")
    tags = relationship("QuestionTagModel", secondary="question_tag_association")
    answer_choices = relationship("AnswerChoiceModel", back_populates="question")
    question_sets = relationship("QuestionSetModel", secondary=question_set_question, back_populates="questions")
    sessions = relationship("SessionQuestionModel", back_populates="question")

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
