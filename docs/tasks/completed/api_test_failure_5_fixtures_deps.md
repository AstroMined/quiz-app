# API Test Failure Analysis 5: Fixtures and Dependencies

## Priority: High
**Branch:** `fix/api-test-failures`
**Estimated Time:** 2-3 hours

## Problem Summary

Multiple test failures indicate fundamental issues with test fixtures and data dependencies. These failures suggest that test setup is not creating the required data correctly, leading to missing dependencies and invalid references.

## Failing Tests Analysis

### Authentication/Role Issues
```
ERROR backend/tests/integration/api/test_disciplines.py::test_create_discipline 
- fastapi.exceptions.HTTPException: 400: Invalid role_id: 1

ERROR backend/tests/integration/api/test_disciplines.py::test_get_nonexistent_discipline 
- ValueError: User not found
```

### Missing Data Structure Issues  
```
ERROR backend/tests/integration/api/test_leaderboard.py::test_get_leaderboard_with_limit 
- KeyError: 'answer_choices'
```

## Detailed Error Analysis

### Role/User Management Issues

**Problem 1: Invalid role_id**
- Test is trying to use `role_id: 1` but this role doesn't exist
- Indicates the default role fixture is not being created properly
- May affect user creation and authentication throughout tests

**Problem 2: User not found**
- Suggests user fixture creation is failing
- Could be due to role dependency issues
- May indicate fixture ordering problems

### Data Structure Issues

**Problem 3: Missing 'answer_choices' key**
- Leaderboard tests expect response data to include 'answer_choices'
- Could be a serialization issue in leaderboard responses
- May indicate missing relationship loading in queries

## Root Cause Investigation Required

### 1. User and Role Fixture Analysis

**Files to examine:**
- `backend/tests/fixtures/models/test_users.py` - User fixtures
- `backend/tests/fixtures/models/test_roles.py` - Role fixtures  
- `backend/tests/conftest.py` - Fixture registration and dependencies
- `backend/app/models/users.py` - User model relationships
- `backend/app/models/roles.py` - Role model definition

**Key Questions:**
- Is the default role fixture being created before user fixtures?
- Are role and user fixtures properly registered in conftest.py?
- Is there a circular dependency in fixture creation?
- Are fixtures being created in the correct database session?

### 2. Leaderboard Data Structure Issues

**Files to examine:**
- `backend/app/api/endpoints/leaderboard.py` - Leaderboard endpoints
- `backend/app/crud/crud_leaderboard.py` - Leaderboard queries
- `backend/app/schemas/leaderboard.py` - Leaderboard response schemas
- `backend/tests/fixtures/models/test_leaderboard.py` - Leaderboard fixtures

**Key Questions:**
- What data structure is expected in leaderboard responses?
- Is the response schema missing the 'answer_choices' field?
- Are leaderboard queries properly loading related data?
- Is the test expectation correct or is the implementation missing data?

### 3. Fixture Dependency Management

**Files to examine:**
- `backend/tests/conftest.py` - Main fixture configuration
- All fixture files in `backend/tests/fixtures/models/`
- Fixture usage patterns across test files

**Key Questions:**
- Are fixtures properly isolated between tests?
- Is test database cleanup happening correctly?
- Are fixture dependencies declared correctly?
- Is there proper order of fixture creation?

## Implementation Plan

### Phase 1: Fixture Dependency Analysis (45 minutes)
1. **Role and User Fixture Review:**
   - Examine role fixture creation and registration
   - Check user fixture dependencies on roles
   - Verify fixture ordering in conftest.py

2. **Database Session Management:**
   - Check if fixtures are using the correct database session
   - Verify transaction handling in fixture creation
   - Ensure proper test isolation

3. **Fixture Reliability Testing:**
   - Run fixture creation tests in isolation
   - Check if fixtures can be created consistently
   - Verify fixture cleanup between tests

### Phase 2: User/Role System Fix (60 minutes)
1. **Role Fixture Creation:**
   - Ensure default role fixture creates roles properly
   - Fix any role creation issues or dependencies
   - Verify role data persistence

2. **User Fixture Dependencies:**
   - Fix user fixture to properly depend on role fixture
   - Ensure users are created with valid role references
   - Fix any user creation failures

3. **Authentication Integration:**
   - Verify authenticated client fixtures work properly
   - Check if login process uses correct user/role data
   - Fix any authentication fixture issues

### Phase 3: Leaderboard Data Structure Fix (45 minutes)
1. **Response Schema Analysis:**
   - Examine expected vs actual leaderboard response structure
   - Determine if 'answer_choices' should be included
   - Check other related response schemas for consistency

2. **Query and Serialization Fix:**
   - Fix leaderboard queries to include required data
   - Update response serialization if needed
   - Ensure consistent data structure across endpoints

3. **Test Expectation Validation:**
   - Verify test expectations match actual requirements
   - Update tests if expectations are incorrect
   - Ensure test data setup creates proper relationships

### Phase 4: Fixture System Optimization (30 minutes)
1. **Dependency Declaration:**
   - Ensure all fixture dependencies are properly declared
   - Fix any circular dependencies
   - Optimize fixture creation order

2. **Test Isolation:**
   - Verify test database cleanup
   - Ensure fixtures are properly scoped
   - Fix any data persistence issues between tests

### Phase 5: Integration Testing (30 minutes)
1. **Cross-Module Testing:**
   - Run tests across different modules to verify fixtures work
   - Check for any remaining dependency issues
   - Verify no regressions in other tests

2. **Full Test Suite Validation:**
   - Run complete test suite to check for improvement
   - Identify any remaining fixture-related issues

## Expected Files to Modify

### High Probability:
- `backend/tests/conftest.py` - Fixture registration and dependencies
- `backend/tests/fixtures/models/test_roles.py` - Role fixture fixes
- `backend/tests/fixtures/models/test_users.py` - User fixture fixes
- `backend/app/api/endpoints/leaderboard.py` - Response structure fixes

### Possible:
- `backend/app/schemas/leaderboard.py` - Schema definition fixes
- `backend/app/crud/crud_leaderboard.py` - Query fixes
- Other fixture files if dependency issues are widespread

## Success Criteria

### User/Role System:
- [ ] Default role fixture creates roles successfully
- [ ] User fixtures properly reference valid roles
- [ ] `test_create_discipline` doesn't fail with "Invalid role_id"
- [ ] `test_get_nonexistent_discipline` doesn't fail with "User not found"

### Leaderboard Data Structure:
- [ ] `test_get_leaderboard_with_limit` doesn't fail with KeyError
- [ ] Leaderboard responses include expected data structure
- [ ] Response schema matches test expectations

### Fixture Reliability:
- [ ] All fixtures can be created consistently
- [ ] Test isolation works properly
- [ ] No circular dependency issues
- [ ] Fixtures are created in correct order

### Overall Validation:
- [ ] Disciplines tests pass (no role/user issues)
- [ ] Leaderboard tests pass (no data structure issues)
- [ ] Other tests don't regress due to fixture changes
- [ ] Test suite runs more reliably overall

## Testing Commands

```bash
# Test specific failing tests
uv run pytest backend/tests/integration/api/test_disciplines.py::test_create_discipline -v
uv run pytest backend/tests/integration/api/test_disciplines.py::test_get_nonexistent_discipline -v
uv run pytest backend/tests/integration/api/test_leaderboard.py::test_get_leaderboard_with_limit -v

# Test fixture creation in isolation
uv run pytest backend/tests/fixtures/ -v

# Test full suites after fixes
uv run pytest backend/tests/integration/api/test_disciplines.py -v
uv run pytest backend/tests/integration/api/test_leaderboard.py -v

# Run broader test to check for regressions
uv run pytest backend/tests/integration/api/ -v
```

## Notes

- These are foundational issues that may be blocking other tests
- Role/user issues could affect many authentication-dependent tests
- Fixture problems often have cascading effects across multiple test modules
- May need to be addressed before other task fixes to ensure proper test environment
- Could reveal deeper issues with database setup or model relationships

## Dependencies

- This task may need to be completed before other tasks if fixture issues are widespread
- May coordinate with Task 1 (Authentication) if user/role issues affect auth tests
- May coordinate with Task 4 (User Responses) if fixture issues affect those tests
- No external dependencies expected

## Priority Notes

Consider completing this task FIRST if:
- Multiple other tasks are failing due to fixture issues
- User/role creation is affecting authentication tests
- Test environment is unreliable due to fixture problems

The other tasks may be easier to complete once the fixture foundation is solid.