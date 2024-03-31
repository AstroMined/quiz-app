# filename: app/db/session.py
"""
This module provides database session management.

It includes functions for creating database engines, sessions, and handling database connections.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base

# Development database
SQLALCHEMY_DATABASE_URL = "sqlite:///./quiz_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """
    Initialize the database.

    This function creates all the tables defined in the models.
    """
    Base.metadata.create_all(bind=engine)

def get_db() -> SessionLocal:
    """
    Get a database session.

    This function creates a new database session and closes it when the request is finished.

    Yields:
        SessionLocal: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
