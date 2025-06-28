# API Test Failure Analysis 3: Question Sets Internal Server Errors

## Priority: High
**Branch:** `fix/api-test-failures`
**Estimated Time:** 3-4 hours

## Problem Summary

Multiple question set endpoints are returning 500 Internal Server Errors where success (200) or proper error codes (404, 400) are expected. This indicates critical implementation issues in the question set management functionality.

## Failing Tests Analysis

### Update Operation Failures (500 Instead of Success)
```
FAILED backend/tests/integration/api/test_question_sets.py::test_update_question_set_endpoint - assert 500 == 200
FAILED backend/tests/integration/api/test_question_sets.py::test_update_question_set_with_multiple_questions - assert 500 == 200
FAILED backend/tests/integration/api/test_question_sets.py::test_update_question_set_remove_questions - assert 500 == 200
```

### Error Handling Failures (500 Instead of Proper Errors)
```
FAILED backend/tests/integration/api/test_question_sets.py::test_update_question_set_not_found - assert 500 == 404
FAILED backend/tests/integration/api/test_question_sets.py::test_update_question_set_invalid_question_ids - assert 500 == 400
```

## Test Data Analysis

### Update Test Example (`test_update_question_set_endpoint`, lines 141-159):
```python
data = {
    "name": "Updated Question Set",
    "question_ids": [test_model_questions[0].id, test_model_questions[1].id],
}
response = logged_in_client.put(f"/question-sets/{test_model_question_set.id}", json=data)
# Expected: 200, Actual: 500
```

### Invalid Question IDs Test (`test_update_question_set_invalid_question_ids`, lines 227-238):
```python
data = {
    "name": "Updated Question Set",
    "question_ids": [999],  # Non-existent question ID
}
response = logged_in_client.put(f"/question-sets/{test_model_question_set.id}", json=data)
# Expected: 400, Actual: 500
```

## Root Cause Investigation Required

### 1. Question Set Update Implementation

**Files to examine:**
- `backend/app/api/endpoints/question_sets.py` - Question set endpoints
- `backend/app/crud/crud_question_sets.py` - Question set CRUD operations
- `backend/app/schemas/question_sets.py` - Question set schemas

**Key Questions:**
- Is the `PUT /question-sets/{id}` endpoint implemented correctly?
- How are `question_ids` relationships being handled during updates?
- Is there proper error handling for database constraint violations?

### 2. Database Relationship Management

**Files to examine:**
- `backend/app/models/question_sets.py` - Question set model
- `backend/app/models/associations.py` - Many-to-many relationships
- Database migration files for question set relationships

**Key Questions:**
- How is the many-to-many relationship between questions and question sets implemented?
- Are relationship updates causing SQL constraint violations?
- Is there proper transaction handling for relationship updates?

### 3. Validation and Error Handling

**Key Questions:**
- Is input validation happening before database operations?
- Are invalid question IDs being caught and returning proper 400 errors?
- Are missing question sets being caught and returning proper 404 errors?
- Is there proper exception handling in the update operations?

## Implementation Plan

### Phase 1: Error Reproduction and Analysis (45 minutes)
1. **Run Individual Tests:**
   - Execute each failing test individually with verbose output
   - Capture the actual 500 error messages and stack traces
   - Identify the exact line where exceptions are occurring

2. **Examine API Endpoint:**
   - Review `PUT /question-sets/{id}` implementation
   - Check request validation and parameter handling
   - Verify response serialization

### Phase 2: CRUD Operation Investigation (60 minutes)
1. **Question Set CRUD Analysis:**
   - Examine `update_question_set_in_db` function
   - Check how `question_ids` are processed and validated
   - Review relationship management logic

2. **Database Model Review:**
   - Verify Question Set model relationships
   - Check many-to-many association table configuration
   - Review any custom update methods or properties

### Phase 3: Relationship Management Deep Dive (60 minutes)
1. **Many-to-Many Relationship Handling:**
   - How are existing question relationships removed?
   - How are new question relationships added?
   - Is there proper batch processing for relationship updates?

2. **Transaction Management:**
   - Are updates wrapped in proper database transactions?
   - Is rollback handling implemented for failed updates?

### Phase 4: Validation and Error Handling (45 minutes)
1. **Input Validation:**
   - Verify question ID validation before database operations
   - Check if non-existent questions are properly detected
   - Ensure proper error messages for validation failures

2. **Exception Handling:**
   - Add proper try-catch blocks for database operations
   - Implement proper HTTP status code returns
   - Ensure meaningful error messages

### Phase 5: Fix Implementation (90 minutes)
1. **Database Operation Fixes:**
   - Fix relationship update logic
   - Implement proper transaction handling
   - Add error handling for constraint violations

2. **Validation Improvements:**
   - Add pre-validation for question IDs
   - Implement proper 404 handling for missing question sets
   - Add proper 400 handling for invalid input

3. **Error Response Standardization:**
   - Ensure consistent error response format
   - Return appropriate HTTP status codes
   - Provide meaningful error messages

### Phase 6: Testing and Validation (30 minutes)
1. **Individual Test Verification:**
   - Run each previously failing test
   - Verify proper status codes and responses

2. **Integration Testing:**
   - Run full question set test suite
   - Check for regressions in related functionality

## Expected Files to Modify

### High Probability:
- `backend/app/api/endpoints/question_sets.py` - Endpoint error handling
- `backend/app/crud/crud_question_sets.py` - Update operation logic
- `backend/app/schemas/question_sets.py` - Validation improvements

### Possible:
- `backend/app/models/question_sets.py` - Model relationship fixes
- `backend/app/models/associations.py` - Association table fixes

## Success Criteria

### Update Operation Success (500 → 200):
- [ ] `test_update_question_set_endpoint` returns 200 OK
- [ ] `test_update_question_set_with_multiple_questions` returns 200 OK
- [ ] `test_update_question_set_remove_questions` returns 200 OK

### Proper Error Handling (500 → Proper Error):
- [ ] `test_update_question_set_not_found` returns 404 Not Found
- [ ] `test_update_question_set_invalid_question_ids` returns 400 Bad Request

### Data Integrity:
- [ ] Question set updates actually modify the database correctly
- [ ] Question relationships are properly added/removed
- [ ] No orphaned or invalid relationships are created

### Overall Validation:
- [ ] All question set tests pass
- [ ] No regressions in question or answer choice tests
- [ ] Error messages are meaningful and consistent

## Testing Commands

```bash
# Run all failing question set tests
uv run pytest backend/tests/integration/api/test_question_sets.py -v

# Run specific failing tests
uv run pytest backend/tests/integration/api/test_question_sets.py::test_update_question_set_endpoint -v
uv run pytest backend/tests/integration/api/test_question_sets.py::test_update_question_set_not_found -v

# Run all question set tests after fixes
uv run pytest backend/tests/integration/api/test_question_sets.py -v

# Check for regressions
uv run pytest backend/tests/integration/api/test_questions.py -v
```

## Notes

- These are critical failures affecting core question set management
- 500 errors suggest fundamental implementation issues rather than edge cases
- May require careful transaction handling for relationship updates
- Could be related to database migration or model configuration issues
- The update functionality appears to be completely broken, not just edge cases

## Dependencies

- May coordinate with Task 2 (Questions) if there are shared relationship issues
- No external dependencies expected
- May require database inspection to understand current state