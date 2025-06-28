# Test Refactoring Task 7: Service Test Separation

## Objective
Separate service tests into unit tests (business logic) and integration tests (database/external dependencies) based on their dependencies and testing focus.

## Background
The current `test_services/` directory contains mixed tests - some test pure business logic (suitable for unit tests) while others test services that interact with databases or external systems (suitable for integration tests).

## Current Service Test Files
Based on directory listing, we have service tests for:
- `test_auth_utils.py`
- `test_authentication_service.py` ✅ Reviewed - uses database
- `test_authorization_service.py`
- `test_logging_service.py`
- `test_permission_generator_service.py`
- `test_randomization_service.py` ✅ Reviewed - pure business logic
- `test_scoring_service.py`
- `test_user_service.py`
- `test_validation_service.py`

## Analysis of Service Test Types

### Unit Test Candidates (Pure Business Logic)
From initial review:
- `test_randomization_service.py` ✅ Pure logic, no external dependencies
- `test_auth_utils.py` (likely utility functions)
- `test_logging_service.py` (if it tests log formatting, not persistence)
- `test_scoring_service.py` (if it tests calculation logic)
- `test_validation_service.py` (if it tests validation rules)

### Integration Test Candidates (Database/External Dependencies)
From initial review:
- `test_authentication_service.py` ✅ Uses database session
- `test_authorization_service.py` (likely checks database permissions)
- `test_user_service.py` (likely CRUD operations)
- `test_permission_generator_service.py` (likely database operations)

## Task Details

### 1. Analyze Each Service Test File
For each service test file, determine its testing focus:

```bash
# Check for database dependencies
grep -r "db_session\|Session\|commit\|query" backend/tests/test_services/

# Check for external API calls
grep -r "requests\|http\|api\|client" backend/tests/test_services/

# Check for pure logic tests
grep -r "assert.*==" backend/tests/test_services/ | grep -v "db_session"
```

### 2. Create Analysis Categories

#### Category A: Pure Unit Tests (Move to `unit/services/`)
Tests that:
- Have no database dependencies
- Test pure business logic and calculations
- Use in-memory objects only
- Execute quickly (< 1ms per test)
- Have no external service calls

**Example Pattern:**
```python
def test_randomization_logic():
    """Test pure randomization business logic."""
    input_list = [1, 2, 3, 4, 5]
    result = randomize_questions(input_list)
    
    # Test business logic only
    assert set(result) == set(input_list)
    assert len(result) == len(input_list)
```

#### Category B: Database Integration Tests (Move to `integration/services/`)
Tests that:
- Use database session fixtures
- Test service interactions with database
- Verify data persistence through services
- Test transaction handling
- Execute slower due to database operations

**Example Pattern:**
```python
def test_authentication_service_with_database(db_session, test_user):
    """Test authentication service with database integration."""
    result = authenticate_user(db_session, test_user.username, "password")
    
    # Test database integration
    assert result is not False
    assert result.id == test_user.id
```

#### Category C: External Service Integration Tests (Move to `integration/services/`)
Tests that:
- Call external APIs or services
- Test service-to-service communication
- May require network access or mocking external services

### 3. Move Pure Unit Tests

#### Step 3a: Identify Pure Unit Tests
```bash
# Create list of files that are pure unit tests
# Based on analysis, move files like:
mv backend/tests/test_services/test_randomization_service.py backend/tests/unit/services/test_randomization.py

# For auth_utils (if pure utility functions)
mv backend/tests/test_services/test_auth_utils.py backend/tests/unit/services/test_auth_utils.py

# Add other pure logic tests as identified
```

#### Step 3b: Clean Up Unit Test Names
Remove redundant `_service` suffix where appropriate:
- `test_randomization_service.py` → `test_randomization.py`
- `test_scoring_service.py` → `test_scoring.py` (if unit test)

### 4. Move Integration Tests

#### Step 4a: Move Database-Dependent Tests
```bash
# Move database integration tests
mv backend/tests/test_services/test_authentication_service.py backend/tests/integration/services/test_authentication.py
mv backend/tests/test_services/test_authorization_service.py backend/tests/integration/services/test_authorization.py
mv backend/tests/test_services/test_user_service.py backend/tests/integration/services/test_user.py
mv backend/tests/test_services/test_permission_generator_service.py backend/tests/integration/services/test_permission_generator.py
```

#### Step 4b: Handle Mixed Tests
Some service files may contain both unit and integration tests. For these:

1. **Split the file** into separate unit and integration test files
2. **Extract pure logic** to unit tests
3. **Keep database/external dependencies** in integration tests

**Example Split:**
```python
# Original test_scoring_service.py contains:
def test_calculate_score():  # Pure logic → unit test
def test_save_score_to_db():  # Database → integration test

# Split into:
# unit/services/test_scoring.py - contains test_calculate_score()
# integration/services/test_scoring.py - contains test_save_score_to_db()
```

### 5. Update Test Content (If Needed)
Some tests may need minor updates to work in new locations:

#### Unit Test Updates
```python
# Ensure no database dependencies
def test_validation_logic():
    """Test validation rules without database."""
    # Use in-memory objects
    test_data = {"field": "value"}
    result = validate_data(test_data)
    assert result.is_valid
```

#### Integration Test Updates
```python
# Ensure proper database integration
def test_service_database_integration(db_session, test_fixtures):
    """Test service with database operations."""
    result = service_function(db_session, test_data)
    db_session.commit()
    
    # Verify persistence
    retrieved = db_session.query(Model).filter_by(id=result.id).first()
    assert retrieved is not None
```

### 6. Remove Empty Directory
After migration, remove the old `test_services/` directory:
```bash
rmdir backend/tests/test_services/
```

## Testing Strategy

### Verify Unit Tests Are Pure
```bash
# Run unit service tests
uv run pytest backend/tests/unit/services/ -v

# Verify no database dependencies
grep -r "db_session\|Session" backend/tests/unit/services/ || echo "No database dependencies"

# Verify fast execution
time uv run pytest backend/tests/unit/services/ -v
```

### Verify Integration Tests Use Database
```bash
# Run integration service tests
uv run pytest backend/tests/integration/services/ -v

# Verify database usage
grep -r "db_session" backend/tests/integration/services/ | wc -l

# Verify slower execution (acceptable for integration tests)
time uv run pytest backend/tests/integration/services/ -v
```

### Run Full Test Suite
```bash
# Ensure overall test suite still works
uv run pytest backend/tests/ -v --tb=short
```

## Success Criteria
- [ ] Service tests separated into unit and integration categories
- [ ] Unit tests moved to `backend/tests/unit/services/`
- [ ] Integration tests moved to `backend/tests/integration/services/`
- [ ] File names cleaned up appropriately
- [ ] Mixed tests split into separate files where needed
- [ ] Unit tests have no database dependencies
- [ ] Integration tests properly use database fixtures
- [ ] All tests pass in new locations
- [ ] Old `test_services/` directory removed
- [ ] Full test suite still passes

## Implementation Notes
- **Analyze Before Moving**: Understand each test's dependencies first
- **Split Mixed Files**: Don't hesitate to split files with mixed concerns
- **Preserve Logic**: Keep all existing test assertions and logic
- **Update Imports**: Ensure imports work in new locations
- **Maintain Performance**: Unit tests should be fast, integration tests may be slower

## Service Test Categories

### Expected Unit Test Services
- **Randomization**: Pure algorithm testing
- **Validation**: Business rule testing  
- **Scoring**: Calculation logic testing
- **Auth Utils**: Utility function testing

### Expected Integration Test Services
- **Authentication**: Database user verification
- **Authorization**: Permission checking with database
- **User Service**: User CRUD operations
- **Permission Generator**: Database permission creation

## Common Patterns

### Unit Test Pattern
```python
def test_business_logic_function():
    """Test pure business logic without external dependencies."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = business_function(input_data)
    
    # Assert
    assert result.meets_business_rules()
    assert result.calculated_value == expected_value
```

### Integration Test Pattern
```python
def test_service_database_interaction(db_session, test_fixtures):
    """Test service interaction with database."""
    # Arrange
    service = ServiceClass(db_session)
    
    # Act
    result = service.perform_operation(test_data)
    db_session.commit()
    
    # Assert
    assert result.id is not None
    # Verify database state
    db_record = db_session.query(Model).filter_by(id=result.id).first()
    assert db_record.field == expected_value
```

## Next Task
After completion, move to `test_refactoring_8_finalize_organization.md` to handle remaining test directories and finalize the refactoring.

## Testing Commands
```bash
# Analysis commands
find backend/tests/test_services/ -name "*.py" -exec grep -l "db_session" {} \;  # Database tests
find backend/tests/test_services/ -name "*.py" -exec grep -L "db_session" {} \;  # Potential unit tests

# Verification commands
uv run pytest backend/tests/unit/services/ -v  # Unit tests
uv run pytest backend/tests/integration/services/ -v  # Integration tests
find backend/tests/unit/services/ -name "*.py" | wc -l  # Count unit test files
find backend/tests/integration/services/ -name "*.py" | wc -l  # Count integration test files
```