# Test Refactoring Task 2: Schema Unit Tests

## Objective
Migrate existing schema tests to the new `unit/schemas/` directory as they are already proper unit tests that follow the "Real Objects Testing Philosophy" without external dependencies.

## Background
The current `test_schemas/` directory contains pure unit tests that validate Pydantic schemas without database dependencies. These tests are exemplary unit tests and will serve as the foundation for our new unit test structure.

## Current Schema Tests
Based on directory listing, we have schema tests for:
- `test_schemas_answer_choices.py`
- `test_schemas_concepts.py`
- `test_schemas_disciplines.py`
- `test_schemas_domains.py`
- `test_schemas_filters.py`
- `test_schemas_groups.py`
- `test_schemas_leaderboard.py`
- `test_schemas_permissions.py`
- `test_schemas_question_sets.py`
- `test_schemas_question_tags.py`
- `test_schemas_questions.py` ✅ Already reviewed - excellent unit test example
- `test_schemas_roles.py`
- `test_schemas_subjects.py`
- `test_schemas_subtopics.py`
- `test_schemas_time_period.py`
- `test_schemas_topics.py`
- `test_schemas_user.py`
- `test_schemas_user_responses.py`

## Task Details

### 1. Verify Schema Tests Are Pure Unit Tests
Before migration, verify that all schema tests follow unit test principles:
- No database session fixtures (`db_session`)
- No external API calls
- Only test Pydantic validation and serialization
- Use in-memory objects and test fixtures

Sample command to check for database dependencies:
```bash
grep -r "db_session\|Session\|database" backend/tests/test_schemas/
```

### 2. Create Unit Test Structure First
Ensure the foundation from Task 1 is complete:
```bash
# Verify new directory structure exists
ls -la backend/tests/unit/schemas/
ls -la backend/tests/integration/
```

### 3. Move Schema Tests to Unit Directory
Move each schema test file to the new unit structure:

```bash
# Move schema tests to unit directory
mv backend/tests/test_schemas/test_schemas_answer_choices.py backend/tests/unit/schemas/test_answer_choices.py
mv backend/tests/test_schemas/test_schemas_concepts.py backend/tests/unit/schemas/test_concepts.py
mv backend/tests/test_schemas/test_schemas_disciplines.py backend/tests/unit/schemas/test_disciplines.py
mv backend/tests/test_schemas/test_schemas_domains.py backend/tests/unit/schemas/test_domains.py
mv backend/tests/test_schemas/test_schemas_filters.py backend/tests/unit/schemas/test_filters.py
mv backend/tests/test_schemas/test_schemas_groups.py backend/tests/unit/schemas/test_groups.py
mv backend/tests/test_schemas/test_schemas_leaderboard.py backend/tests/unit/schemas/test_leaderboard.py
mv backend/tests/test_schemas/test_schemas_permissions.py backend/tests/unit/schemas/test_permissions.py
mv backend/tests/test_schemas/test_schemas_question_sets.py backend/tests/unit/schemas/test_question_sets.py
mv backend/tests/test_schemas/test_schemas_question_tags.py backend/tests/unit/schemas/test_question_tags.py
mv backend/tests/test_schemas/test_schemas_questions.py backend/tests/unit/schemas/test_questions.py
mv backend/tests/test_schemas/test_schemas_roles.py backend/tests/unit/schemas/test_roles.py
mv backend/tests/test_schemas/test_schemas_subjects.py backend/tests/unit/schemas/test_subjects.py
mv backend/tests/test_schemas/test_schemas_subtopics.py backend/tests/unit/schemas/test_subtopics.py
mv backend/tests/test_schemas/test_schemas_time_period.py backend/tests/unit/schemas/test_time_period.py
mv backend/tests/test_schemas/test_schemas_topics.py backend/tests/unit/schemas/test_topics.py
mv backend/tests/test_schemas/test_schemas_user.py backend/tests/unit/schemas/test_user.py
mv backend/tests/test_schemas/test_schemas_user_responses.py backend/tests/unit/schemas/test_user_responses.py
```

### 4. Clean Up File Names
Remove the redundant `test_schemas_` prefix since they're now clearly in the schemas directory:
- File names should follow pattern: `test_{component}.py`
- This improves readability and follows pytest conventions

### 5. Update Any Import References
Check if any other test files import from the old schema test locations:
```bash
grep -r "from.*test_schemas" backend/tests/
grep -r "import.*test_schemas" backend/tests/
```

### 6. Remove Empty Directory
After migration, remove the old `test_schemas/` directory:
```bash
rmdir backend/tests/test_schemas/
```

## Testing Strategy

### Verify Unit Tests Work in New Location
```bash
# Run only the migrated schema unit tests
uv run pytest backend/tests/unit/schemas/ -v

# Verify they run fast (unit test characteristic)
time uv run pytest backend/tests/unit/schemas/ -v

# Check no database dependencies
uv run pytest backend/tests/unit/schemas/ -v --tb=short | grep -i "session\|database" || echo "No database dependencies found"
```

### Run Full Test Suite
```bash
# Ensure overall test suite still works
uv run pytest backend/tests/ -v --tb=short
```

## Success Criteria
- [ ] All schema tests moved to `backend/tests/unit/schemas/`
- [ ] File names cleaned up (remove `test_schemas_` prefix)
- [ ] All moved tests pass in new location
- [ ] No database dependencies in unit tests
- [ ] Old `test_schemas/` directory removed
- [ ] Full test suite still passes
- [ ] Tests run quickly (< 5 seconds for all schema tests)

## Implementation Notes
- Schema tests are already excellent unit tests - minimal changes needed
- Focus on moving and renaming rather than rewriting
- Preserve all existing test logic and assertions
- Ensure pytest discovery works with new file paths
- Validate that fixtures still work correctly in new location

## Common Issues to Watch For
1. **Import path changes**: Verify relative imports still work
2. **Fixture discovery**: Ensure fixtures from `conftest.py` are still accessible
3. **Naming conflicts**: Check that shortened file names don't conflict
4. **Test discovery**: Verify pytest finds all tests in new location

## Next Task
After completion, move to `test_refactoring_3_model_unit_tests.md` to extract pure unit tests from the current model tests.

## Testing Commands
```bash
# Quick verification commands
find backend/tests/unit/schemas/ -name "*.py" | wc -l  # Should show 18 files
uv run pytest backend/tests/unit/schemas/test_questions.py -v  # Test one specific file
uv run pytest backend/tests/unit/ -v  # Test all unit tests so far
```