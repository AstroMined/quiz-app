# Test Refactoring Task 4: CRUD Integration Tests

## Objective
Move existing CRUD tests to the `integration/crud/` directory as they are proper integration tests that verify database operations with real database connections.

## Background
The current `test_crud/` directory contains integration tests that validate CRUD (Create, Read, Update, Delete) operations through the database layer. These tests properly use database sessions and test cross-component interactions, making them exemplary integration tests.

## Current CRUD Test Files
Based on directory listing, we have CRUD tests for:
- `test_crud_answer_choices.py`
- `test_crud_authentication.py`
- `test_crud_concepts.py`
- `test_crud_disciplines.py`
- `test_crud_domains.py`
- `test_crud_filters.py`
- `test_crud_groups.py`
- `test_crud_leaderboard.py`
- `test_crud_permissions.py`
- `test_crud_question_sets.py`
- `test_crud_question_tags.py`
- `test_crud_questions.py`
- `test_crud_roles.py`
- `test_crud_subjects.py`
- `test_crud_subtopics.py`
- `test_crud_topics.py`
- `test_crud_user.py`
- `test_crud_user_responses.py`

## Task Details

### 1. Verify CRUD Tests Are Proper Integration Tests
Before migration, verify that CRUD tests follow integration test principles:
- Use database session fixtures (`db_session`)
- Test real database operations (INSERT, SELECT, UPDATE, DELETE)
- Test data persistence and retrieval
- Test foreign key relationships and constraints
- Use real SQLAlchemy model instances

Sample verification command:
```bash
grep -r "db_session\|create.*in_db\|get.*from_db" backend/tests/test_crud/ | head -10
```

### 2. Move CRUD Tests to Integration Directory
Move each CRUD test file to the new integration structure:

```bash
# Move CRUD tests to integration directory
mv backend/tests/test_crud/test_crud_answer_choices.py backend/tests/integration/crud/test_answer_choices.py
mv backend/tests/test_crud/test_crud_authentication.py backend/tests/integration/crud/test_authentication.py
mv backend/tests/test_crud/test_crud_concepts.py backend/tests/integration/crud/test_concepts.py
mv backend/tests/test_crud/test_crud_disciplines.py backend/tests/integration/crud/test_disciplines.py
mv backend/tests/test_crud/test_crud_domains.py backend/tests/integration/crud/test_domains.py
mv backend/tests/test_crud/test_crud_filters.py backend/tests/integration/crud/test_filters.py
mv backend/tests/test_crud/test_crud_groups.py backend/tests/integration/crud/test_groups.py
mv backend/tests/test_crud/test_crud_leaderboard.py backend/tests/integration/crud/test_leaderboard.py
mv backend/tests/test_crud/test_crud_permissions.py backend/tests/integration/crud/test_permissions.py
mv backend/tests/test_crud/test_crud_question_sets.py backend/tests/integration/crud/test_question_sets.py
mv backend/tests/test_crud/test_crud_question_tags.py backend/tests/integration/crud/test_question_tags.py
mv backend/tests/test_crud/test_crud_questions.py backend/tests/integration/crud/test_questions.py
mv backend/tests/test_crud/test_crud_roles.py backend/tests/integration/crud/test_roles.py
mv backend/tests/test_crud/test_crud_subjects.py backend/tests/integration/crud/test_subjects.py
mv backend/tests/test_crud/test_crud_subtopics.py backend/tests/integration/crud/test_subtopics.py
mv backend/tests/test_crud/test_crud_topics.py backend/tests/integration/crud/test_topics.py
mv backend/tests/test_crud/test_crud_user.py backend/tests/integration/crud/test_user.py
mv backend/tests/test_crud/test_crud_user_responses.py backend/tests/integration/crud/test_user_responses.py
```

### 3. Clean Up File Names
Remove the redundant `test_crud_` prefix since they're now clearly in the crud directory:
- Files should follow pattern: `test_{component}.py`
- This improves readability and follows the new directory structure

### 4. Verify Database Integration Test Characteristics
Ensure moved tests demonstrate proper integration test patterns:

#### Example Integration Test Pattern
```python
def test_create_question_in_db(db_session, test_model_subject, test_model_user):
    """Test creating a question through CRUD layer with database persistence."""
    from backend.app.crud.crud_questions import create_question_in_db
    from backend.app.models.questions import DifficultyLevel
    
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "creator_id": test_model_user.id
    }
    
    # Test database creation
    question = create_question_in_db(db_session, question_data)
    db_session.commit()
    
    # Verify persistence
    assert question.id is not None
    assert question.text == "What is the capital of France?"
    
    # Verify database retrieval
    retrieved_question = db_session.query(QuestionModel).filter_by(id=question.id).first()
    assert retrieved_question is not None
    assert retrieved_question.text == question.text
```

### 5. Update Any Import References
Check if any other test files import from the old CRUD test locations:
```bash
grep -r "from.*test_crud" backend/tests/
grep -r "import.*test_crud" backend/tests/
```

### 6. Remove Empty Directory
After migration, remove the old `test_crud/` directory:
```bash
rmdir backend/tests/test_crud/
```

## Testing Strategy

### Verify Integration Tests Work in New Location
```bash
# Run only the migrated CRUD integration tests
uv run pytest backend/tests/integration/crud/ -v

# Verify they use database properly (slower execution expected)
time uv run pytest backend/tests/integration/crud/ -v

# Check for proper database usage
uv run pytest backend/tests/integration/crud/ -v -s | grep -i "session\|database" | head -5
```

### Test Database Isolation
```bash
# Verify test isolation (each test should start with clean state)
uv run pytest backend/tests/integration/crud/test_questions.py -v --tb=short
```

### Run Full Test Suite
```bash
# Ensure overall test suite still works
uv run pytest backend/tests/ -v --tb=short
```

## Success Criteria
- [ ] All CRUD tests moved to `backend/tests/integration/crud/`
- [ ] File names cleaned up (remove `test_crud_` prefix)
- [ ] All moved tests pass in new location
- [ ] Tests demonstrate proper database integration patterns
- [ ] Old `test_crud/` directory removed
- [ ] Full test suite still passes
- [ ] Tests properly use database fixtures and sessions
- [ ] Test execution time reflects integration test nature (slower than unit tests)

## Implementation Notes
- CRUD tests are already proper integration tests - minimal changes needed
- Focus on moving and renaming rather than rewriting
- Preserve all existing database test logic and assertions
- Ensure pytest discovery works with new file paths
- Validate that database fixtures still work correctly in new location
- Maintain test isolation between database tests

## Integration Test Characteristics to Verify
1. **Database Sessions**: All tests should use `db_session` fixture
2. **Real Data Persistence**: Tests should verify data survives database operations
3. **Foreign Key Relationships**: Tests should validate database constraints
4. **Transaction Handling**: Tests should properly commit/rollback transactions
5. **Data Integrity**: Tests should verify business rules at database level

## Common Issues to Watch For
1. **Fixture Scope**: Ensure database fixtures have correct scope for isolation
2. **Transaction Rollback**: Verify test cleanup doesn't affect other tests
3. **Foreign Key Dependencies**: Ensure test data creation order is correct
4. **Database Connection**: Verify database connection is properly managed
5. **Test Isolation**: Each test should start with predictable database state

## Next Task
After completion, move to `test_refactoring_5_api_integration_tests.md` to reorganize API endpoint tests as integration tests.

## Testing Commands
```bash
# Quick verification commands
find backend/tests/integration/crud/ -name "*.py" | wc -l  # Should show 18 files
uv run pytest backend/tests/integration/crud/test_questions.py -v  # Test one specific file
uv run pytest backend/tests/integration/ -v  # Test all integration tests so far
```