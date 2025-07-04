# filename: backend/tests/fixtures/database/session_fixtures.py

import os
import toml
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.main import app
from backend.app.crud.crud_time_period import init_time_periods_in_db
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.models.domains import DomainModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.subjects import SubjectModel
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

# Global cache for reference data per worker
_reference_data_cache = {}


def create_default_roles(session) -> dict:
    """
    Create default roles and permissions required for testing.
    
    Adapted from production init_db() function to provide essential
    reference data for test scenarios.
    
    Args:
        session: SQLAlchemy session for database operations
        
    Returns:
        dict: Dictionary containing created roles keyed by name
        
    Raises:
        RuntimeError: If role creation fails
    """
    try:
        # Create permissions (essential set for testing)
        permissions_data = [
            {"name": "read__docs", "description": "Read documentation"},
            {"name": "read__redoc", "description": "Read Redoc documentation"},
            {"name": "read__openapi.json", "description": "Read OpenAPI specification"},
            {"name": "read__", "description": "Read root endpoint"},
            {"name": "create__login", "description": "Login authentication"},
            {"name": "create__register_", "description": "User registration"},
            {"name": "read__users_me", "description": "Read own user profile"},
            {"name": "update__users_me", "description": "Update own user profile"},
            {"name": "create__questions", "description": "Create questions"},
            {"name": "read__questions", "description": "Read questions"},
            {"name": "update__questions", "description": "Update questions"},
            {"name": "delete__questions", "description": "Delete questions"},
            {"name": "create__subjects", "description": "Create subjects"},
            {"name": "read__subjects", "description": "Read subjects"},
        ]
        
        # Create permission objects
        permissions = {}
        for perm_data in permissions_data:
            # Check if permission already exists
            existing_perm = session.query(PermissionModel).filter_by(name=perm_data["name"]).first()
            if existing_perm:
                permissions[perm_data["name"]] = existing_perm
            else:
                perm = PermissionModel(**perm_data)
                session.add(perm)
                permissions[perm_data["name"]] = perm
        
        session.flush()  # Get IDs for relationships
        
        # Create roles with permission assignments
        user_permission_names = [
            "read__docs", "read__redoc", "read__openapi.json", "read__",
            "create__login", "create__register_", "read__users_me", "update__users_me"
        ]
        user_permissions = [permissions[name] for name in user_permission_names if name in permissions]
        
        admin_permission_names = user_permission_names + [
            "create__questions", "read__questions", "update__questions",
            "create__subjects", "read__subjects"
        ]
        admin_permissions = [permissions[name] for name in admin_permission_names if name in permissions]
        
        # All permissions for superadmin
        superadmin_permissions = list(permissions.values())
        
        # Check for existing roles and create if needed
        roles = {}
        
        # User role (default)
        existing_user_role = session.query(RoleModel).filter_by(name="user").first()
        if existing_user_role:
            roles["user"] = existing_user_role
        else:
            user_role = RoleModel(
                name="user",
                description="Regular User",
                permissions=user_permissions,
                default=True
            )
            session.add(user_role)
            roles["user"] = user_role
        
        # Admin role
        existing_admin_role = session.query(RoleModel).filter_by(name="admin").first()
        if existing_admin_role:
            roles["admin"] = existing_admin_role
        else:
            admin_role = RoleModel(
                name="admin",
                description="Administrator",
                permissions=admin_permissions,
                default=False
            )
            session.add(admin_role)
            roles["admin"] = admin_role
        
        # Superadmin role
        existing_superadmin_role = session.query(RoleModel).filter_by(name="superadmin").first()
        if existing_superadmin_role:
            roles["superadmin"] = existing_superadmin_role
        else:
            superadmin_role = RoleModel(
                name="superadmin",
                description="Super Administrator",
                permissions=superadmin_permissions,
                default=False
            )
            session.add(superadmin_role)
            roles["superadmin"] = superadmin_role
        
        session.commit()
        return roles
        
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Failed to create default roles: {e}")


def create_content_hierarchy(session) -> dict:
    """
    Create basic content hierarchy for testing.
    
    Creates a minimal but complete content hierarchy including domains,
    disciplines, and subjects with proper many-to-many relationships
    for test scenarios.
    
    Args:
        session: SQLAlchemy session for database operations
        
    Returns:
        dict: Dictionary containing created content hierarchy data
        
    Raises:
        RuntimeError: If content hierarchy creation fails
    """
    try:
        # Create domains
        domains = {}
        domain_data = [
            {"name": "STEM", "description": "Science, Technology, Engineering, Mathematics"},
            {"name": "Humanities", "description": "Liberal arts and humanities"},
            {"name": "Social Sciences", "description": "Social sciences and related fields"}
        ]
        
        for domain_info in domain_data:
            existing_domain = session.query(DomainModel).filter_by(name=domain_info["name"]).first()
            if existing_domain:
                domains[domain_info["name"].lower().replace(" ", "_")] = existing_domain
            else:
                domain = DomainModel(name=domain_info["name"])
                session.add(domain)
                domains[domain_info["name"].lower().replace(" ", "_")] = domain
        
        session.flush()  # Get IDs for relationships
        
        # Create disciplines
        disciplines = {}
        discipline_data = [
            {"name": "Mathematics", "domain_key": "stem"},
            {"name": "Computer Science", "domain_key": "stem"}, 
            {"name": "Physics", "domain_key": "stem"},
            {"name": "History", "domain_key": "humanities"},
            {"name": "Literature", "domain_key": "humanities"},
            {"name": "Psychology", "domain_key": "social_sciences"}
        ]
        
        for disc_info in discipline_data:
            existing_discipline = session.query(DisciplineModel).filter_by(name=disc_info["name"]).first()
            if existing_discipline:
                disciplines[disc_info["name"].lower().replace(" ", "_")] = existing_discipline
            else:
                discipline = DisciplineModel(name=disc_info["name"])
                # Set up domain relationship
                if disc_info["domain_key"] in domains:
                    discipline.domains = [domains[disc_info["domain_key"]]]
                session.add(discipline)
                disciplines[disc_info["name"].lower().replace(" ", "_")] = discipline
        
        session.flush()  # Get IDs for relationships
        
        # Create subjects
        subjects = {}
        subject_data = [
            {"name": "Algebra", "discipline_key": "mathematics"},
            {"name": "Calculus", "discipline_key": "mathematics"},
            {"name": "Geometry", "discipline_key": "mathematics"},
            {"name": "Algorithms", "discipline_key": "computer_science"},
            {"name": "Data Structures", "discipline_key": "computer_science"},
            {"name": "Classical Mechanics", "discipline_key": "physics"},
            {"name": "World War II", "discipline_key": "history"},
            {"name": "American Literature", "discipline_key": "literature"},
            {"name": "Cognitive Psychology", "discipline_key": "psychology"}
        ]
        
        for subj_info in subject_data:
            existing_subject = session.query(SubjectModel).filter_by(name=subj_info["name"]).first()
            if existing_subject:
                subjects[subj_info["name"].lower().replace(" ", "_")] = existing_subject
            else:
                subject = SubjectModel(name=subj_info["name"])
                # Set up discipline relationship
                if subj_info["discipline_key"] in disciplines:
                    subject.disciplines = [disciplines[subj_info["discipline_key"]]]
                session.add(subject)
                subjects[subj_info["name"].lower().replace(" ", "_")] = subject
        
        session.commit()
        
        return {
            "domains": domains,
            "disciplines": disciplines,
            "subjects": subjects
        }
        
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Failed to create content hierarchy: {e}")


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
            "isolation_level": None,
        },
        poolclass=StaticPool,
        echo=False
    )
    
    # Enable foreign key constraints for all connections
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Create all tables once per worker session
    Base.metadata.create_all(bind=engine)
    
    return engine


@pytest.fixture(scope="session") 
def session_factory(test_engine):
    """Create a session factory for the test session."""
    return sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session")
def verify_constraints(test_engine):
    """Verify that foreign key constraints are properly enabled."""
    from sqlalchemy import text
    
    with test_engine.connect() as conn:
        result = conn.execute(text("PRAGMA foreign_keys"))
        fk_enabled = result.fetchone()[0]
        assert fk_enabled == 1, "Foreign key constraints must be enabled for proper testing"
    
    return True


@pytest.fixture(scope="session")
def base_reference_data(test_engine, verify_constraints):
    """Initialize comprehensive reference data once per worker test session."""
    global _reference_data_initialized, _reference_data_cache
    
    worker_id = get_worker_id()
    
    if not _reference_data_initialized.get(worker_id, False):
        SessionLocal = sessionmaker(bind=test_engine)
        session = SessionLocal()
        try:
            # Initialize all reference data types
            roles = create_default_roles(session)
            content_hierarchy = create_content_hierarchy(session)
            init_time_periods_in_db(session)
            
            # Store reference data for fixture access
            _reference_data_cache[worker_id] = {
                "roles": roles,
                "content_hierarchy": content_hierarchy
            }
            
            session.commit()
            _reference_data_initialized[worker_id] = True
            
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to initialize reference data: {e}")
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


# Reference Data Access Fixtures

@pytest.fixture(scope="session")
def default_role(base_reference_data, test_engine):
    """Get the default user role for testing."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        role = session.query(RoleModel).filter_by(default=True).first()
        if not role:
            raise RuntimeError("Default role not found - reference data not initialized")
        return role
    finally:
        session.close()


@pytest.fixture(scope="session") 
def admin_role(base_reference_data, test_engine):
    """Get the admin role for testing."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal() 
    try:
        role = session.query(RoleModel).filter_by(name="admin").first()
        if not role:
            raise RuntimeError("Admin role not found - reference data not initialized")
        return role
    finally:
        session.close()


@pytest.fixture(scope="session")
def superadmin_role(base_reference_data, test_engine):
    """Get the superadmin role for testing."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        role = session.query(RoleModel).filter_by(name="superadmin").first()
        if not role:
            raise RuntimeError("Superadmin role not found - reference data not initialized")
        return role
    finally:
        session.close()


@pytest.fixture(scope="session")
def test_disciplines(base_reference_data, test_engine):
    """Get test disciplines for content organization tests."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        disciplines = session.query(DisciplineModel).all()
        if not disciplines:
            raise RuntimeError("Disciplines not found - reference data not initialized")
        return disciplines
    finally:
        session.close()


@pytest.fixture(scope="session")
def test_subjects(base_reference_data, test_engine):
    """Get test subjects for content organization tests."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        subjects = session.query(SubjectModel).all()
        if not subjects:
            raise RuntimeError("Subjects not found - reference data not initialized")
        return subjects
    finally:
        session.close()


@pytest.fixture(scope="session")
def test_domains(base_reference_data, test_engine):
    """Get test domains for content organization tests."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        domains = session.query(DomainModel).all()
        if not domains:
            raise RuntimeError("Domains not found - reference data not initialized")
        return domains
    finally:
        session.close()


@pytest.fixture(scope="session")
def mathematics_discipline(base_reference_data, test_engine):
    """Get the Mathematics discipline for specific tests."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        discipline = session.query(DisciplineModel).filter_by(name="Mathematics").first()
        if not discipline:
            raise RuntimeError("Mathematics discipline not found - reference data not initialized")
        return discipline
    finally:
        session.close()


@pytest.fixture(scope="session")
def algebra_subject(base_reference_data, test_engine):
    """Get the Algebra subject for specific tests."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        subject = session.query(SubjectModel).filter_by(name="Algebra").first()
        if not subject:
            raise RuntimeError("Algebra subject not found - reference data not initialized")
        return subject
    finally:
        session.close()