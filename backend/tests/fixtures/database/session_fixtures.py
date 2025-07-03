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
from backend.tests.helpers.fixture_performance import track_fixture_performance

# Load the test database URL from pyproject.toml for compatibility
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
    "pyproject.toml"
)
config = toml.load(config_path)
# Use in-memory database for significant performance improvement
IN_MEMORY_DATABASE_URL = "sqlite:///:memory:"

# Global cache for reference data initialization per worker
_reference_data_initialized = {}

# Global storage for current test database session (thread-local doesn't work with FastAPI TestClient)
_current_test_session = None


def get_worker_id():
    """Get the current pytest-xdist worker ID, or 'main' for non-parallel execution."""
    try:
        # Try to get worker ID from pytest-xdist
        import pytest
        if hasattr(pytest, 'current_node') and pytest.current_node:
            worker_input = getattr(pytest.current_node, 'workerinput', {})
            return worker_input.get('workerid', 'main')
    except (ImportError, AttributeError):
        pass
    
    # Fallback for non-parallel execution
    return 'main'


@pytest.fixture(scope="session")
def test_engine():
    """Create a worker-specific in-memory database engine for the test session."""
    worker_id = get_worker_id()
    
    # Create unique database URL for each worker to ensure complete isolation
    if worker_id == 'main':
        database_url = IN_MEMORY_DATABASE_URL
    else:
        # Add worker ID as query parameter to create separate databases per worker
        database_url = f"{IN_MEMORY_DATABASE_URL}?worker={worker_id}"
    
    engine = create_engine(
        database_url,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables once per worker session
    Base.metadata.create_all(bind=engine)
    
    return engine


@pytest.fixture(scope="session") 
def session_factory(test_engine):
    """Create a session factory for the test session."""
    return sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session")
def base_reference_data(test_engine):
    """Initialize reference data once per worker test session."""
    global _reference_data_initialized
    
    worker_id = get_worker_id()
    
    if not _reference_data_initialized.get(worker_id, False):
        SessionLocal = sessionmaker(bind=test_engine)
        session = SessionLocal()
        try:
            # Initialize time periods and other static data
            init_time_periods_in_db(session)
            session.commit()
            _reference_data_initialized[worker_id] = True
        finally:
            session.close()
    
    return True


@pytest.fixture(scope="function")
@track_fixture_performance(scope="function")
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
@track_fixture_performance(scope="function")
def client(db_session, test_engine):
    """
    Provide a test client with transaction-scoped database session override.
    
    IMPROVED SOLUTION: This fixture uses the real FastAPI app instance while ensuring
    middleware and endpoints share the same test database session. This eliminates
    the need to recreate the app while solving the session mismatch problem.
    
    The approach:
    1. Uses the real production FastAPI app (maintains all production behaviors)
    2. Overrides dependency injection for endpoints
    3. Temporarily overrides middleware database functions during tests
    4. Restores original middleware functions after tests
    """
    from backend.app.main import app
    from backend.app.db.session import get_db
    from backend.app.middleware.blacklist_middleware import BlacklistMiddleware
    from backend.app.middleware.authorization_middleware import AuthorizationMiddleware
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
    """Global middleware database function that returns the current test session."""
    global _current_test_session
    
    # Get the current test session from global storage
    if _current_test_session is not None:
        try:
            yield _current_test_session
        finally:
            # Session cleanup handled by db_session fixture
            pass
    else:
        # Fallback - should not happen in normal test execution
        from backend.app.db.session import get_db
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()


@pytest.fixture(scope="function")
@track_fixture_performance(scope="function")
def client(db_session, test_engine):
    """
    Provide a test client with transaction-scoped database session override.
    
    IMPROVED SOLUTION: This fixture uses the real FastAPI app instance while ensuring
    middleware and endpoints share the same test database session. This eliminates
    the need to recreate the app while solving the session mismatch problem.
    
    The approach:
    1. Uses the real production FastAPI app (maintains all production behaviors)
    2. Overrides dependency injection for endpoints
    3. Uses thread-local storage to provide current test session to middleware
    4. Dynamically updates middleware to use current test session
    """
    from backend.app.main import app
    from backend.app.db.session import get_db
    from backend.app.middleware.blacklist_middleware import BlacklistMiddleware
    from backend.app.middleware.authorization_middleware import AuthorizationMiddleware
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

    # Store the current test session in global storage for middleware access
    global _current_test_session
    _current_test_session = wrapped_session
    
    # Override dependency injection for endpoints
    app.dependency_overrides[get_db] = override_get_db
    
    # Find and temporarily override middleware database functions (one-time setup)
    middleware_originals = []
    
    for middleware_item in app.user_middleware:
        if hasattr(middleware_item, 'cls'):
            middleware_cls = middleware_item.cls
            if middleware_cls in (BlacklistMiddleware, AuthorizationMiddleware):
                # Check if middleware has get_db_func parameter
                if hasattr(middleware_item, 'kwargs') and 'get_db_func' in middleware_item.kwargs:
                    # Check current function and override if needed
                    current_func = middleware_item.kwargs['get_db_func']
                    if current_func != test_get_db_for_middleware:
                        # Store original function for restoration
                        middleware_originals.append((middleware_item, current_func))
                        # Override with global test function
                        middleware_item.kwargs['get_db_func'] = test_get_db_for_middleware
                        logger.debug(f"Overrode {middleware_cls.__name__} database function for tests")
    
    logger.debug(f"Using real FastAPI app with {len(middleware_originals)} middleware overrides")
    
    # Ensure the session stays in global storage during the entire test
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Clean up global session after test completes
        _current_test_session = None
        
        # Restore original middleware database functions (only if we overrode them this time)
        for middleware_item, original_func in middleware_originals:
            middleware_item.kwargs['get_db_func'] = original_func
            logger.debug(f"Restored {type(middleware_item.cls).__name__} database function")
    
    app.dependency_overrides.clear()