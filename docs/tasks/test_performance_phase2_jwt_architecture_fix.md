# Test Performance Phase 2: JWT Architecture Fix

## Overview
Address the critical architectural issue blocking transaction-based test isolation by refactoring JWT creation to use proper dependency injection instead of direct database access.

## Problem Analysis

### Current Architectural Issue (BLOCKING)
- **Location**: `backend/app/core/jwt.py:23`
- **Issue**: `db = next(get_db())` bypasses FastAPI dependency injection
- **Impact**: Creates new database session outside test transaction scope
- **Consequence**: Prevents transaction rollback approach, forcing expensive database resets

### Current Code Pattern
```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    # ... token expiration logic ...
    
    db = next(get_db())  # PROBLEM: Direct database access
    user = read_user_by_username_from_db(db, to_encode["sub"])
    if not user:
        raise ValueError("User not found")
    # ... rest of token creation ...
```

### Impact on Test Performance
- Forces use of file-based database resets instead of transaction rollback
- Prevents 70-80% additional performance improvement
- Blocks implementation of in-memory database optimization

## Implementation Tasks

### Task 1: Refactor JWT Creation Function
**Objective**: Remove direct `get_db()` call and accept database session as parameter

**Target Implementation**:
```python
def create_access_token(data: dict, db: Session, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Use provided session instead of creating new one
    user = read_user_by_username_from_db(db, to_encode["sub"])
    if not user:
        raise ValueError("User not found")

    to_encode.update({
        "exp": expire,
        "user_id": user.id,
        "jti": str(uuid.uuid4()),
    })

    encoded_jwt = jwt.encode(to_encode, settings_core.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

### Task 2: Update All JWT Function Callers
**Objective**: Update all code that calls `create_access_token` to pass database session

**Files to Update**:
1. `backend/app/api/endpoints/authentication.py` - Login endpoint
2. Any other endpoints that create tokens
3. Service layer functions that generate tokens

**Example Update** (`authentication.py`):
```python
# Before
access_token = create_access_token(
    data={"remember_me": form_data.remember_me, "sub": user.username}
)

# After  
access_token = create_access_token(
    data={"remember_me": form_data.remember_me, "sub": user.username},
    db=db
)
```

### Task 3: Audit for Other Direct Database Access
**Objective**: Find and fix any other instances of direct `get_db()` calls in business logic

**Search Pattern**: `next(get_db())`
**Scope**: All business logic files (services, core modules)

### Task 4: Implement Transaction-Based Test Isolation
**Objective**: Once JWT issue is fixed, implement transaction rollback in test fixtures

**Target Implementation** (`session_fixtures.py`):
```python
@pytest.fixture(scope="function")
def db_session():
    """Provide a clean database session using transaction rollback."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    try:
        init_time_periods_in_db(session)
        session.flush()
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
```

## Expected Performance Impact

### After JWT Architecture Fix
- **Database Approach**: In-memory SQLite with transaction rollback
- **Single API Test Time**: 0.3-0.7 seconds (down from current 1.5-1.7s)
- **Total Additional Improvement**: 70-80% reduction on top of Phase 1 gains
- **Combined Improvement**: 80-85% total improvement from original baseline

### Performance Calculation
- **Original**: ~2.2 seconds per test
- **Phase 1**: ~1.6 seconds per test (27% improvement)
- **Phase 2 Target**: ~0.4 seconds per test (75% additional improvement)
- **Total Target**: 82% improvement from baseline

## Implementation Steps

1. **Analyze Current JWT Usage**
   - Map all callers of `create_access_token`
   - Identify function signatures that need database access
   - Document current token creation workflow

2. **Refactor JWT Functions**
   - Update `create_access_token` to accept database session
   - Test JWT functionality with updated signature
   - Ensure token validation still works

3. **Update All Callers**
   - Modify authentication endpoints to pass database session
   - Update any service layer functions
   - Verify all authentication flows still work

4. **Audit Business Logic**
   - Search for other direct `get_db()` usage
   - Refactor any additional instances found
   - Ensure proper dependency injection throughout

5. **Implement Transaction Isolation**
   - Update test fixtures to use transaction rollback
   - Switch to in-memory database
   - Test with subset of API tests first

6. **Performance Validation**
   - Measure before/after test execution times
   - Verify 70-80% additional improvement achieved
   - Run full test suite to ensure stability

## Acceptance Criteria

- [ ] `create_access_token` no longer calls `next(get_db())` directly
- [ ] All authentication endpoints pass database session to JWT functions
- [ ] No direct `get_db()` calls remain in business logic
- [ ] All existing authentication tests pass
- [ ] Transaction-based test isolation implemented
- [ ] In-memory database successfully configured
- [ ] API test execution time reduced by at least 60% from Phase 1 baseline
- [ ] Full test suite passes with new architecture

## Risks and Mitigation

**Risk**: Breaking authentication functionality during refactor
**Mitigation**: Incremental changes with test validation at each step

**Risk**: Missed instances of direct database access
**Mitigation**: Comprehensive code search and systematic review

**Risk**: Transaction isolation issues with complex test scenarios
**Mitigation**: Gradual rollout starting with simple test cases

## Dependencies

**Requires**: Phase 1 completion (foundation test optimizations)
**Enables**: Phase 3 parallel execution (requires proper test isolation)
**Blocks**: Cannot achieve full performance potential without this fix

## Success Impact

This architectural fix is the key to unlocking the full performance potential of the test suite. Without it, we're limited to the 25-33% improvement from Phase 1. With it, we can achieve the target 80-85% total improvement and enable advanced optimizations like parallel execution.