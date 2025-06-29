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
# Use original file-based database for compatibility, but with optimizations
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
    from backend.app.db.session import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            # Don't close the session here - let db_session fixture handle cleanup
            pass

    # Override dependency injection for endpoints
    app.dependency_overrides[get_db] = override_get_db
    
    # Override middleware database access - access the actual middleware instances
    middleware_originals = []
    
    # The middleware instances are stored in app.user_middleware
    for middleware_wrapper in app.user_middleware:
        # The actual middleware instance is stored in the args of the wrapper
        if hasattr(middleware_wrapper, 'args') and middleware_wrapper.args:
            middleware_instance = middleware_wrapper.args[0]  # First arg is the middleware instance
            if hasattr(middleware_instance, 'get_db_func'):
                # Store original function
                original_func = middleware_instance.get_db_func
                middleware_originals.append((middleware_instance, original_func))
                # Override with test function
                middleware_instance.get_db_func = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore original middleware database functions
    for middleware_instance, original_func in middleware_originals:
        middleware_instance.get_db_func = original_func
    
    app.dependency_overrides.clear()