# filename: app/models/user_responses.py
"""
This module defines the UserResponse model.

The UserResponse model represents a user's response to a question in the quiz app.
"""

from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime
from app.db.base_class import Base

class UserResponse(Base):
    """
    The UserResponse model.

    Attributes:
        id (int): The primary key of the user response.
        user_id (int): The foreign key referencing the associated user.
        question_id (int): The foreign key referencing the associated question.
        answer_choice_id (int): The foreign key referencing the associated answer choice.
        is_correct (bool): Indicates whether the user's response is correct.
        timestamp (datetime): The timestamp of the user's response.
        user (User): The relationship to the associated user.
        question (Question): The relationship to the associated question.
        answer_choice (AnswerChoice): The relationship to the associated answer choice.
    """
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_choice_id = Column(Integer, ForeignKey('answer_choices.id'))
    is_correct = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="responses")
    question = relationship("Question")
    answer_choice = relationship("AnswerChoice")