# Test Refactoring Task 5: API Integration Tests

## Objective
Move existing API tests to the `integration/api/` directory as they are proper integration tests that verify full request/response cycles through the FastAPI application stack.

## Background
The current `test_api/` directory contains integration tests that validate API endpoints through the complete application stack. These tests use FastAPI test clients and verify end-to-end request/response handling, making them exemplary integration tests.

## Current API Test Files
Based on directory listing, we have API tests for:
- `test_api_answer_choices.py`
- `test_api_authentication.py`
- `test_api_concepts.py`
- `test_api_disciplines.py`
- `test_api_domains.py`
- `test_api_filters.py`
- `test_api_groups.py`
- `test_api_leaderboard.py`
- `test_api_question_sets.py`
- `test_api_question_tags.py`
- `test_api_questions.py` ✅ Already reviewed
- `test_api_register.py`
- `test_api_subjects.py`
- `test_api_subtopics.py`
- `test_api_topics.py`
- `test_api_user_responses.py`
- `test_api_users.py`

## Task Details

### 1. Verify API Tests Are Proper Integration Tests
Before migration, verify that API tests follow integration test principles:
- Use FastAPI test client (`logged_in_client`, `client`)
- Test complete HTTP request/response cycles
- Verify status codes, response structure, and data
- Test authentication and authorization flows
- Integrate with database through API layer

Sample verification command:
```bash
grep -r "client\|response\|status_code\|\.post\|\.get\|\.put\|\.delete" backend/tests/test_api/ | head -10
```

### 2. Move API Tests to Integration Directory
Move each API test file to the new integration structure:

```bash
# Move API tests to integration directory
mv backend/tests/test_api/test_api_answer_choices.py backend/tests/integration/api/test_answer_choices.py
mv backend/tests/test_api/test_api_authentication.py backend/tests/integration/api/test_authentication.py
mv backend/tests/test_api/test_api_concepts.py backend/tests/integration/api/test_concepts.py
mv backend/tests/test_api/test_api_disciplines.py backend/tests/integration/api/test_disciplines.py
mv backend/tests/test_api/test_api_domains.py backend/tests/integration/api/test_domains.py
mv backend/tests/test_api/test_api_filters.py backend/tests/integration/api/test_filters.py
mv backend/tests/test_api/test_api_groups.py backend/tests/integration/api/test_groups.py
mv backend/tests/test_api/test_api_leaderboard.py backend/tests/integration/api/test_leaderboard.py
mv backend/tests/test_api/test_api_question_sets.py backend/tests/integration/api/test_question_sets.py
mv backend/tests/test_api/test_api_question_tags.py backend/tests/integration/api/test_question_tags.py
mv backend/tests/test_api/test_api_questions.py backend/tests/integration/api/test_questions.py
mv backend/tests/test_api/test_api_register.py backend/tests/integration/api/test_register.py
mv backend/tests/test_api/test_api_subjects.py backend/tests/integration/api/test_subjects.py
mv backend/tests/test_api/test_api_subtopics.py backend/tests/integration/api/test_subtopics.py
mv backend/tests/test_api/test_api_topics.py backend/tests/integration/api/test_topics.py
mv backend/tests/test_api/test_api_user_responses.py backend/tests/integration/api/test_user_responses.py
mv backend/tests/test_api/test_api_users.py backend/tests/integration/api/test_users.py
```

### 3. Clean Up File Names
Remove the redundant `test_api_` prefix since they're now clearly in the api directory:
- Files should follow pattern: `test_{endpoint}.py`
- This improves readability and follows the new directory structure

### 4. Verify API Integration Test Characteristics
Ensure moved tests demonstrate proper API integration test patterns:

#### Example API Integration Test Pattern
```python
def test_create_question_endpoint(logged_in_client, test_model_subject, test_model_topic):
    """Test question creation through API endpoint with full request/response cycle."""
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": "Easy",
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [],
        "concept_ids": []
    }

    # Test API request
    response = logged_in_client.post("/questions/", json=question_data)
    
    # Verify HTTP response
    assert response.status_code == 201
    
    # Verify response structure and data
    created_question = response.json()
    assert created_question["text"] == "What is the capital of France?"
    assert created_question["difficulty"] == "Easy"
    assert "id" in created_question
    
    # Verify data persistence through API
    get_response = logged_in_client.get(f"/questions/{created_question['id']}")
    assert get_response.status_code == 200
    retrieved_question = get_response.json()
    assert retrieved_question["text"] == question_data["text"]
```

### 5. Verify Authentication and Authorization Testing
API tests should include proper authentication flows:

#### Authentication Test Patterns
```python
def test_authenticated_endpoint(logged_in_client):
    """Test endpoint requires authentication."""
    response = logged_in_client.get("/protected-endpoint/")
    assert response.status_code == 200

def test_unauthenticated_access(client):
    """Test endpoint rejects unauthenticated requests."""
    response = client.get("/protected-endpoint/")
    assert response.status_code == 401

def test_authorization_levels(logged_in_client, admin_client):
    """Test different authorization levels."""
    # Regular user access
    response = logged_in_client.delete("/admin-only-endpoint/1")
    assert response.status_code == 403
    
    # Admin access
    response = admin_client.delete("/admin-only-endpoint/1")
    assert response.status_code == 200
```

### 6. Update Any Import References
Check if any other test files import from the old API test locations:
```bash
grep -r "from.*test_api" backend/tests/
grep -r "import.*test_api" backend/tests/
```

### 7. Remove Empty Directory
After migration, remove the old `test_api/` directory:
```bash
rmdir backend/tests/test_api/
```

## Testing Strategy

### Verify API Integration Tests Work in New Location
```bash
# Run only the migrated API integration tests
uv run pytest backend/tests/integration/api/ -v

# Verify they test full HTTP cycles (may be slower due to API stack)
time uv run pytest backend/tests/integration/api/ -v

# Check for proper API testing patterns
uv run pytest backend/tests/integration/api/ -v -s | grep -i "status_code\|response\|client" | head -5
```

### Test Authentication Flows
```bash
# Verify authentication tests work
uv run pytest backend/tests/integration/api/test_authentication.py -v
uv run pytest backend/tests/integration/api/test_register.py -v
```

### Test Specific API Endpoints
```bash
# Test individual API endpoint files
uv run pytest backend/tests/integration/api/test_questions.py -v
uv run pytest backend/tests/integration/api/test_users.py -v
```

### Run Full Test Suite
```bash
# Ensure overall test suite still works
uv run pytest backend/tests/ -v --tb=short
```

## Success Criteria
- [ ] All API tests moved to `backend/tests/integration/api/`
- [ ] File names cleaned up (remove `test_api_` prefix)
- [ ] All moved tests pass in new location
- [ ] Tests demonstrate proper API integration patterns
- [ ] Authentication and authorization flows tested
- [ ] HTTP status codes and response validation working
- [ ] Old `test_api/` directory removed
- [ ] Full test suite still passes
- [ ] Test client fixtures work correctly in new location

## Implementation Notes
- API tests are already proper integration tests - minimal changes needed
- Focus on moving and renaming rather than rewriting
- Preserve all existing API test logic and assertions
- Ensure pytest discovery works with new file paths
- Validate that client fixtures (`logged_in_client`, `client`) still work correctly
- Maintain authentication state between test methods

## API Integration Test Characteristics to Verify
1. **HTTP Clients**: All tests should use FastAPI test client fixtures
2. **Request/Response Cycles**: Tests should verify complete HTTP flows
3. **Status Code Validation**: Tests should assert proper HTTP status codes
4. **JSON Serialization**: Tests should verify request/response JSON handling
5. **Authentication**: Tests should verify authentication and authorization
6. **Error Handling**: Tests should verify proper error responses
7. **Data Validation**: Tests should verify Pydantic schema validation through API

## Common Issues to Watch For
1. **Client Fixtures**: Ensure test client fixtures have correct scope
2. **Authentication State**: Verify logged-in state persists across test methods
3. **Database State**: API tests should clean up database changes
4. **JSON Serialization**: Verify datetime and enum serialization works
5. **Error Responses**: Ensure error status codes and messages are tested
6. **Request Headers**: Verify Content-Type and Authorization headers

## Next Task
After completion, move to `test_refactoring_6_model_integration_tests.md` to move existing model tests to integration directory.

## Testing Commands
```bash
# Quick verification commands
find backend/tests/integration/api/ -name "*.py" | wc -l  # Should show 17 files
uv run pytest backend/tests/integration/api/test_questions.py -v  # Test one specific file
uv run pytest backend/tests/integration/api/test_authentication.py -v  # Test auth flows
uv run pytest backend/tests/integration/ -v  # Test all integration tests so far
```