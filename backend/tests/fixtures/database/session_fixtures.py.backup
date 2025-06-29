# filename: backend/tests/fixtures/database/session_fixtures.py

import os
import toml
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.base import Base
from backend.app.main import app
from backend.app.crud.crud_time_period import init_time_periods_in_db

# Load the test database URL from pyproject.toml
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
    "pyproject.toml"
)
config = toml.load(config_path)
SQLALCHEMY_TEST_DATABASE_URL = config["tool"]["app"]["database_url_test"]


def reset_database(db_url):
    """Reset the test database by dropping and recreating all tables."""
    engine = create_engine(db_url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provide a clean database session for each test."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    reset_database(SQLALCHEMY_TEST_DATABASE_URL)
    session = TestingSessionLocal()
    session.rollback()  # Roll back any existing transaction
    try:
        init_time_periods_in_db(session)
        yield session
    finally:
        session.close()
        reset_database(SQLALCHEMY_TEST_DATABASE_URL)


@pytest.fixture(scope="function")
def client(db_session):
    """Provide a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[override_get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()