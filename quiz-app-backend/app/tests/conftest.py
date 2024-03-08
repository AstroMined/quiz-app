# filename: app/tests/conftest.py
"""
This module defines pytest fixtures for testing the Quiz App backend.

Fixtures are reusable objects that can be used across multiple test files.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from main import app
from app.schemas.user import UserCreate
from app.crud.crud_user import create_user, remove_user
from app.db.session import get_db
import random
import string
from sqlalchemy import create_engine
from app.db.base_class import Base

def random_lower_string() -> str:
    """
    Generate a random lowercase string of length 8.

    Returns:
        str: The generated random string.
    """
    return "".join(random.choices(string.ascii_lowercase, k=8))

@pytest.fixture(scope="session")
def db_session():
    """
    Fixture for creating a database session for testing.

    This fixture creates a new database session using an in-memory SQLite database.
    It yields the session object and cleans up the database after the tests are finished.

    Yields:
        Session: The database session object.
    """
    # Setup for database session
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)  # Create all tables for the test database
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def test_app(db_session):
    """
    Fixture for creating a FastAPI test client.

    This fixture overrides the `get_db` dependency with the test database session.
    It yields the FastAPI app and cleans up the dependency overrides after the tests are finished.

    Yields:
        FastAPI: The FastAPI app instance.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    yield app
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def client(test_app):
    """
    Fixture for creating a FastAPI test client.

    This fixture creates a test client using the FastAPI app fixture.
    It yields the test client object.

    Yields:
        TestClient: The FastAPI test client.
    """
    with TestClient(test_app) as c:
        yield c

@pytest.fixture(scope="session")
def test_user(db_session):
    """
    Fixture for creating a test user.

    This fixture creates a new user in the test database using random credentials.
    It yields the user object and password, and removes the user from the database after the tests are finished.

    Yields:
        tuple: A tuple containing the user object and password.
    """
    db = db_session
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = create_user(db=db, user=user_in)
    db.commit()
    yield user, password
    remove_user(db=db, user_id=user.id)