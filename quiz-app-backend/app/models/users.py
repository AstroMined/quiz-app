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
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Add this line

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    responses = relationship("UserResponse", back_populates="user")
