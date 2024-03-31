# filename: app/models/users.py
"""
This module defines the User model.

The User model represents a user in the quiz app.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    """
    The User model.

    Attributes:
        id (int): The primary key of the user.
        username (str): The username of the user.
        hashed_password (str): The hashed password of the user.
        is_active (bool): Indicates whether the user is active.
        responses (List[UserResponse]): The relationship to the associated user responses.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    responses = relationship("UserResponse", back_populates="user")