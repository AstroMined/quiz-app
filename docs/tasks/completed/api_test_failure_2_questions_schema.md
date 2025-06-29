# API Test Failure Analysis 2: Question Schema Validation Issues

## Priority: High
**Branch:** `fix/api-test-failures`
**Estimated Time:** 3-4 hours

## Problem Summary

Multiple question API endpoints are returning 422 validation errors where 201 (created) or 200 (success) status codes are expected. This indicates fundamental schema validation or data processing issues.

## Failing Tests Analysis

### Primary Failures (422 Instead of Success)
```
FAILED backend/tests/integration/api/test_questions.py::test_create_question - assert 422 == 201
FAILED backend/tests/integration/api/test_questions.py::test_create_question_with_answers - assert 422 == 201
FAILED backend/tests/integration/api/test_questions.py::test_update_question - assert 422 == 200
FAILED backend/tests/integration/api/test_questions.py::test_update_nonexistent_question - assert 422 == 404
FAILED backend/tests/integration/api/test_questions.py::test_update_question_no_changes - assert 422 == 200
FAILED backend/tests/integration/api/test_questions.py::test_update_question_not_found - assert 422 == 404
```

### Secondary Failures (500 Internal Server Error)
```
FAILED backend/tests/integration/api/test_questions.py::test_get_questions - assert 500 == 200
FAILED backend/tests/integration/api/test_questions.py::test_get_question - assert 500 == 200
FAILED backend/tests/integration/api/test_questions.py::test_get_questions_pagination - assert 500 == 200
```

## Root Cause Investigation Required

### 1. Schema Validation Issues (422 Errors)

**Test Data Analysis:**
Looking at `test_create_question` (lines 11-33), the test uses:
```python
question_data = {
    "text": "What is the capital of France?",
    "difficulty": DifficultyLevel.EASY.value,
    "subject_ids": [test_model_subject.id],
    "topic_ids": [test_model_topic.id],
    "subtopic_ids": [test_model_subtopic.id],
    "concept_ids": [test_model_concept.id],
}
```

**Files to examine:**
- `backend/app/schemas/questions.py` - Question schema definitions
- `backend/app/api/endpoints/questions.py` - Question endpoints
- `backend/app/core/config.py` - DifficultyLevel enum definition

**Key Questions:**
- Are the schema field names matching what the API expects?
- Is the DifficultyLevel enum validation working correctly?
- Are the relationship IDs (subject_ids, topic_ids, etc.) being validated properly?
- Are there missing required fields in the schema?

### 2. Internal Server Errors (500 Errors)

**Files to examine:**
- `backend/app/crud/crud_questions.py` - Question CRUD operations
- `backend/app/models/questions.py` - Question model definitions
- Database relationship configurations

**Key Questions:**
- Are there SQL relationship issues causing database errors?
- Are the CRUD operations handling missing relationships properly?
- Is there a serialization issue when returning question data?

### 3. Endpoint Implementation Review

**Files to examine:**
- `backend/app/api/endpoints/questions.py` - All question endpoints
- Response serialization and error handling

## Implementation Plan

### Phase 1: Schema Investigation (60 minutes)
1. **Compare Schema vs Test Data:**
   - Examine `QuestionCreateSchema` in `backend/app/schemas/questions.py`
   - Compare field names and types with test data
   - Check if all required fields are present in tests

2. **Validate Enum Handling:**
   - Verify `DifficultyLevel` enum definition and usage
   - Check if enum values are being properly converted/validated

3. **Relationship Validation:**
   - Examine how `subject_ids`, `topic_ids`, etc. are validated
   - Check if these fields require existing records or just validation

### Phase 2: API Endpoint Analysis (60 minutes)
1. **Question Creation Endpoints:**
   - `POST /questions/` - Basic question creation
   - `POST /questions/with-answers/` - Question with answer choices
   - Check request handling and validation

2. **Question Update Endpoints:**
   - `PUT /questions/{id}` - Question updates
   - Verify path parameter and request body handling

3. **Question Retrieval Endpoints:**
   - `GET /questions/` - List questions with pagination
   - `GET /questions/{id}` - Single question retrieval

### Phase 3: CRUD Operation Review (45 minutes)
1. **Database Operations:**
   - Examine `create_question_in_db` function
   - Check relationship handling in question creation
   - Verify update and retrieval operations

2. **Model Relationships:**
   - Review Question model relationships with Subject, Topic, etc.
   - Check if lazy loading or eager loading is causing issues

### Phase 4: Fix Implementation (90 minutes)
1. **Schema Fixes:**
   - Correct field validation issues
   - Fix enum handling if needed
   - Update relationship validation

2. **API Endpoint Fixes:**
   - Fix request/response handling
   - Improve error handling and messages
   - Ensure proper status code returns

3. **CRUD Operation Fixes:**
   - Fix database operation issues
   - Improve relationship handling
   - Add proper error handling for missing records

### Phase 5: Testing and Validation (45 minutes)
1. **Run Specific Tests:**
   - Test each failing question endpoint individually
   - Verify both success and error cases

2. **Integration Testing:**
   - Run full question test suite
   - Check for regressions in related tests

## Expected Files to Modify

### High Probability:
- `backend/app/schemas/questions.py` - Schema validation fixes
- `backend/app/api/endpoints/questions.py` - Endpoint implementation
- `backend/app/crud/crud_questions.py` - CRUD operation fixes

### Possible:
- `backend/app/models/questions.py` - Model relationship fixes
- `backend/app/core/config.py` - Enum definition issues

## Success Criteria

### Primary Success (422 → Success):
- [ ] `test_create_question` returns 201 Created
- [ ] `test_create_question_with_answers` returns 201 Created  
- [ ] `test_update_question` returns 200 OK
- [ ] `test_update_question_no_changes` returns 200 OK

### Secondary Success (422 → Proper Error):
- [ ] `test_update_nonexistent_question` returns 404 Not Found
- [ ] `test_update_question_not_found` returns 404 Not Found

### Tertiary Success (500 → Success):
- [ ] `test_get_questions` returns 200 OK
- [ ] `test_get_question` returns 200 OK
- [ ] `test_get_questions_pagination` returns 200 OK

### Overall Validation:
- [ ] All question tests pass
- [ ] No regressions in related tests (answer_choices, question_sets)
- [ ] API responses include expected data structure

## Testing Commands

```bash
# Run all failing question tests
uv run pytest backend/tests/integration/api/test_questions.py -v

# Run specific test categories
uv run pytest backend/tests/integration/api/test_questions.py::test_create_question -v
uv run pytest backend/tests/integration/api/test_questions.py::test_get_questions -v

# Run related tests to check for regressions
uv run pytest backend/tests/integration/api/test_answer_choices.py -v
uv run pytest backend/tests/integration/api/test_question_sets.py -v
```

## Notes

- This appears to be a foundational issue affecting core question functionality
- May require coordination with answer_choices and question_sets fixes
- Schema validation errors suggest the issue is in request processing, not business logic
- 500 errors indicate deeper database or model relationship issues

## Dependencies

- May need to coordinate with Task 3 (Question Sets) if there are shared relationship issues
- May need to coordinate with Task 4 (Answer Choices) for question creation with answers
- No external dependencies expected