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
    """Provide a test client with transaction-scoped database session override."""
    from backend.app.db.session import get_db
    
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
    
    def override_get_db_for_middleware():
        """Override for middleware - returns the same wrapped session."""
        # Debug: verify we're using the same session
        from backend.app.services.logging_service import logger
        logger.debug(f"Middleware using session: {wrapped_session}")
        yield wrapped_session

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
                # Override with test function that returns the same session
                middleware_instance.get_db_func = override_get_db_for_middleware
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore original middleware database functions
    for middleware_instance, original_func in middleware_originals:
        middleware_instance.get_db_func = original_func
    
    app.dependency_overrides.clear()