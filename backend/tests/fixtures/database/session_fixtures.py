# filename: backend/tests/fixtures/database/session_fixtures.py

import os
import toml
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.main import app
from backend.app.crud.crud_time_period import init_time_periods_in_db

# Load the test database URL from pyproject.toml for compatibility
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
    "pyproject.toml"
)
config = toml.load(config_path)
# Use in-memory database for significant performance improvement
IN_MEMORY_DATABASE_URL = "sqlite:///:memory:"

# Global cache for reference data initialization
_reference_data_initialized = False


@pytest.fixture(scope="session")
def test_engine():
    """Create a single in-memory database engine for the entire test session."""
    engine = create_engine(
        IN_MEMORY_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables once per session
    Base.metadata.create_all(bind=engine)
    
    return engine


@pytest.fixture(scope="session") 
def session_factory(test_engine):
    """Create a session factory for the test session."""
    return sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session")
def base_reference_data(test_engine):
    """Initialize reference data once per test session."""
    global _reference_data_initialized
    
    if not _reference_data_initialized:
        SessionLocal = sessionmaker(bind=test_engine)
        session = SessionLocal()
        try:
            # Initialize time periods and other static data
            init_time_periods_in_db(session)
            session.commit()
            _reference_data_initialized = True
        finally:
            session.close()
    
    return True


@pytest.fixture(scope="function")
def db_session(test_engine, session_factory, base_reference_data):
    """Provide a clean database session using transaction rollback for isolation."""
    # Create a connection and begin a transaction
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    session = session_factory(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        # Only rollback if transaction is still active
        if transaction.is_active:
            transaction.rollback()  # FAST: Just rollback transaction
        connection.close()


class NoCloseSessionWrapper:
    """Wrapper that prevents session.close() calls during testing."""
    def __init__(self, session):
        self._session = session
    
    def __getattr__(self, name):
        if name == 'close':
            # Ignore close() calls - transaction rollback handles cleanup
            return lambda: None
        return getattr(self._session, name)
    
    def __repr__(self):
        return f"NoCloseSessionWrapper({self._session})"


@pytest.fixture(scope="function")
def client(db_session, test_engine):
    """
    Provide a test client with transaction-scoped database session override.
    
    CRITICAL FIX: This fixture creates a test-specific FastAPI application instance
    to ensure that middleware (BlacklistMiddleware, AuthorizationMiddleware) use 
    the same database session as the test endpoints. This prevents "User not found" 
    errors that occurred when middleware and endpoints used different database sessions.
    
    The fix works by:
    1. Creating a test-specific FastAPI app instead of using the main app
    2. Copying all routes from the main app to the test app  
    3. Adding middleware with explicit database session injection
    4. Ensuring all components (endpoints + middleware) use the same test session
    """
    from fastapi import FastAPI
    from backend.app.db.session import get_db
    from backend.app.middleware.blacklist_middleware import BlacklistMiddleware
    from backend.app.middleware.authorization_middleware import AuthorizationMiddleware
    from backend.app.middleware.cors_middleware import add_cors_middleware
    from backend.app.services.logging_service import logger
    
    # Create a wrapper that ignores close() calls
    wrapped_session = NoCloseSessionWrapper(db_session)
    
    def override_get_db():
        """Override database dependency to use transaction-scoped session."""
        try:
            yield wrapped_session
        finally:
            # Session cleanup handled by db_session fixture
            # CRITICAL: Don't close the session here - it's transaction-scoped
            pass
    
    def test_get_db_for_middleware():
        """Provide the same session for middleware."""
        return override_get_db()

    # Override dependency injection for endpoints
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test-specific application with properly injected middleware
    test_app = FastAPI()
    
    # Add all the same routes as the main app
    for route in app.routes:
        test_app.routes.append(route)
    
    # Add middleware with test database function
    test_app.add_middleware(AuthorizationMiddleware, get_db_func=test_get_db_for_middleware)
    test_app.add_middleware(BlacklistMiddleware, get_db_func=test_get_db_for_middleware)
    add_cors_middleware(test_app)
    
    # Copy dependency overrides to test app
    test_app.dependency_overrides = app.dependency_overrides.copy()
    
    logger.debug("Created test app with middleware using test database session")
    
    with TestClient(test_app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()