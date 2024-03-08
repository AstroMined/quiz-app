# filename: app/db/base_class.py
"""
This module defines the base class for SQLAlchemy models.

It provides a declarative base class that can be used to create database models.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()