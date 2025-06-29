# Test Performance Phase 2.3: Test Infrastructure Overhaul

## Overview
Implement transaction-based test isolation with in-memory database to achieve the target 70-80% performance improvement, now that JWT and middleware architecture supports proper dependency injection.

## Problem Analysis

### Current Test Database Approach (INEFFICIENT)
- **Location**: `backend/tests/fixtures/database/session_fixtures.py:24-46`
- **Issue**: File-based database with full reset between tests
- **Current Pattern**: Drop all tables → Create all tables → Initialize data → Run test → Repeat
- **Performance**: ~1.5-1.7 seconds per API test

### Current Implementation
```python
@pytest.fixture(scope="function")
def db_session():
    """Provide a clean database session for each test."""
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, ...)
    TestingSessionLocal = sessionmaker(...)
    reset_database(SQLALCHEMY_TEST_DATABASE_URL)  # EXPENSIVE: Full table drop/create
    session = TestingSessionLocal()
    session.rollback()
    try:
        init_time_periods_in_db(session)
        yield session
    finally:
        session.close()
        reset_database(SQLALCHEMY_TEST_DATABASE_URL)  # EXPENSIVE: Full reset again
```

### Architectural Readiness (AFTER PHASES 2.1 & 2.2)
- ✅ JWT functions accept database sessions
- ✅ Middleware supports dependency injection
- ✅ No direct `next(get_db())` calls in authentication/authorization
- ✅ Ready for transaction-based isolation

## Implementation Tasks

### Task 1: Implement In-Memory Database with Transaction Rollback
**Objective**: Replace file-based database with in-memory SQLite and transaction rollback

**Target Implementation**:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# In-memory database configuration  
IN_MEMORY_DATABASE_URL = "sqlite:///:memory:"

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

@pytest.fixture(scope="function")
def db_session(test_engine, session_factory):
    """Provide a clean database session using transaction rollback."""
    # Create a connection and begin a transaction
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    session = session_factory(bind=connection)
    
    # Initialize reference data once per session (cached)
    init_time_periods_in_db(session)
    session.flush()  # Ensure reference data is available
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()  # FAST: Just rollback transaction
        connection.close()
```

### Task 2: Optimize Reference Data Initialization
**Objective**: Cache static reference data to avoid recreation on every test

**Target Implementation**:
```python
# Global cache for reference data initialization
_reference_data_initialized = False

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
    """Provide a clean database session with reference data available."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = session_factory(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
```

### Task 3: Update Client Fixture for New Database Architecture
**Objective**: Ensure FastAPI test client uses transaction-scoped database sessions

**Target Implementation**:
```python
@pytest.fixture(scope="function")
def client(db_session, test_engine):
    """Provide a test client with transaction-scoped database session override."""
    from backend.app.db.session import get_db
    from backend.app.main import app
    
    def override_get_db():
        """Override database dependency to use transaction-scoped session."""
        try:
            yield db_session
        finally:
            # Session cleanup handled by db_session fixture
            pass

    # Override dependency injection
    app.dependency_overrides[get_db] = override_get_db
    
    # Override middleware database access (from Phase 2.2)
    for middleware in app.user_middleware:
        if hasattr(middleware.cls, 'get_db_func'):
            middleware.cls.get_db_func = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()
    
    # Reset middleware database functions
    for middleware in app.user_middleware:
        if hasattr(middleware.cls, 'get_db_func'):
            middleware.cls.get_db_func = get_db
```

### Task 4: Create Performance Benchmarking
**Objective**: Measure and validate the performance improvement

**Implementation**:
```python
import time
import pytest
from backend.tests.helpers.performance import PerformanceTracker

@pytest.fixture(scope="session")
def performance_tracker():
    """Track test performance metrics."""
    return PerformanceTracker()

@pytest.fixture(autouse=True)
def track_test_performance(request, performance_tracker):
    """Automatically track performance for all tests."""
    start_time = time.time()
    yield
    end_time = time.time()
    
    test_duration = end_time - start_time
    performance_tracker.record_test(
        test_name=request.node.nodeid,
        duration=test_duration,
        category="api" if "test_api" in str(request.fspath) else "other"
    )

# Add performance assertion helpers
def assert_api_test_performance(duration, max_expected=0.5):
    """Assert that API test completed within performance target."""
    assert duration < max_expected, f"API test took {duration:.3f}s, expected < {max_expected}s"
```

### Task 5: Update Complex Test Fixtures
**Objective**: Optimize complex fixtures to work with transaction rollback

**Target Pattern**:
```python
@pytest.fixture(scope="function")
def complex_quiz_data(db_session):
    """Create complex quiz data within transaction scope."""
    # Create test data that will be automatically rolled back
    subject = create_test_subject(db_session)
    questions = create_test_questions(db_session, subject_id=subject.id, count=10)
    question_set = create_test_question_set(db_session, question_ids=[q.id for q in questions])
    
    db_session.flush()  # Make data available within transaction
    
    return {
        'subject': subject,
        'questions': questions, 
        'question_set': question_set
    }
    # No cleanup needed - transaction rollback handles it
```

## Implementation Steps

1. **Create New Database Architecture**
   - Implement in-memory database with session-scoped engine
   - Create transaction-based session fixtures
   - Add reference data caching

2. **Update Client Fixture**
   - Modify test client to use transaction-scoped sessions
   - Ensure middleware database override works correctly
   - Test basic API endpoint functionality

3. **Add Performance Tracking**
   - Implement performance measurement fixtures
   - Add benchmarking helpers
   - Create performance regression detection

4. **Update Complex Fixtures**
   - Modify existing fixtures to work with transaction rollback
   - Remove unnecessary cleanup code
   - Optimize fixture data creation

5. **Validate with Subset of Tests**
   - Run critical API tests with new infrastructure
   - Measure performance improvement
   - Verify test isolation works correctly

6. **Full Test Suite Migration**
   - Run entire test suite with new infrastructure
   - Fix any compatibility issues
   - Validate 70-80% performance improvement

## Expected Performance Impact

### Before Infrastructure Overhaul (Current)
- **API Test Duration**: 1.5-1.7 seconds per test
- **Database Operations**: File-based with full table reset
- **Isolation Method**: Drop/recreate tables between tests

### After Infrastructure Overhaul (Target)
- **API Test Duration**: 0.3-0.5 seconds per test  
- **Database Operations**: In-memory with transaction rollback
- **Isolation Method**: Transaction rollback (near-instantaneous)

**Expected Improvement**: 70-80% reduction in test execution time
**Combined with Phase 1**: 80-85% total improvement from original baseline

### Performance Calculation
- **Original Baseline**: ~2.2 seconds per test
- **Phase 1 Improvement**: ~1.6 seconds per test (27% improvement)
- **Phase 2.3 Target**: ~0.4 seconds per test (75% additional improvement)
- **Total Target**: 82% improvement from baseline

## Acceptance Criteria

- [ ] In-memory database successfully configured for tests
- [ ] Transaction rollback isolation implemented
- [ ] Reference data initialization optimized (session-scoped)
- [ ] Test client fixture uses transaction-scoped database sessions
- [ ] Middleware database access works with test overrides
- [ ] All existing tests pass with new infrastructure
- [ ] API test execution time reduced by at least 70% from Phase 1 baseline
- [ ] Performance benchmarking and regression detection implemented
- [ ] Complex test fixtures optimized for transaction rollback
- [ ] Test isolation verified (no data leakage between tests)

## Risks and Mitigation

**Risk**: In-memory database behavior differences from file-based SQLite
**Mitigation**: Thorough testing of edge cases, foreign key constraints, and transaction behavior

**Risk**: Transaction rollback not properly isolating test data
**Mitigation**: Extensive test isolation validation, including concurrent access patterns

**Risk**: Reference data initialization causing test dependencies
**Mitigation**: Careful design of session-scoped vs function-scoped data, clear separation of concerns

**Risk**: Middleware database override not working correctly
**Mitigation**: Step-by-step testing of middleware + test client integration

## Dependencies

**Requires**: 
- Phase 2.1 completion (JWT functions accept database sessions)
- Phase 2.2 completion (middleware supports dependency injection)

**Enables**: Phase 2.4 (performance validation) and Phase 3 (parallel execution)

**Critical**: This phase delivers the primary performance improvement target

## Success Impact

This phase delivers the core performance improvement promised by the transaction-based test isolation approach. Success here achieves:

- **70-80% improvement** in test execution speed
- **Foundation for parallel execution** (Phase 3)
- **Sustainable test architecture** for future development
- **Validation of architectural refactoring** from Phases 2.1 and 2.2

**Target**: Single API test execution time drops from 1.6s to 0.4s (75% improvement)