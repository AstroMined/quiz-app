# Fixture Naming Cleanup: Resolve Missing Fixture References

## Task Overview

**Status**: 📋 **Pending**  
**Priority**: Medium  
**Complexity**: Low  
**Estimated Effort**: 1-2 hours  

## Problem Summary

Several test files reference fixtures using the old naming convention (`test_questions`, `test_user`, `test_answer_choices`) instead of the current naming convention (`test_model_questions`, `test_model_user`, `test_model_answer_choices`). This causes immediate test failures due to missing fixture references.

### Current State Problems

1. **Missing Fixture References**: Tests fail with "fixture not found" errors
2. **Naming Convention Mismatch**: Tests use `test_*` but fixtures are named `test_model_*`
3. **Import Dependencies**: Some tests may reference fixtures that don't exist at all

### Evidence from Investigation

```bash
# Error pattern from test runs
E       fixture 'test_questions' not found
>       available fixtures: ... test_model_questions, ...
```

## Root Cause Analysis

### Fixture Naming Evolution

**Historical Context**: The test suite was refactored to follow a cleaner naming convention:
- **Old pattern**: `test_questions`, `test_user`, `test_answer_choices`
- **New pattern**: `test_model_questions`, `test_model_user`, `test_model_answer_choices`

**Current State**: Some test files were updated to use the new convention, others were not.

### Affected Files and Locations

**Primary File**: `backend/tests/integration/api/test_database_error_handling.py`

**Specific Issues Identified**:
- Line 34: `test_questions` → should be `test_model_questions`
- Line 34: `test_answer_choices` → should be `test_model_answer_choices`  
- Line 57: `test_user` → should be `test_model_user`
- Line 57: `test_answer_choices` → should be `test_model_answer_choices`
- Line 80: `test_user` → should be `test_model_user`
- Line 80: `test_questions` → should be `test_model_questions`
- Line 103: `test_group` → should be `test_model_group`
- Line 125: `test_user` → should be `test_model_user`
- Line 147: `test_user` → should be `test_model_user`
- Line 147: `test_group` → should be `test_model_group`
- Line 211: `test_user` → should be `test_model_user`
- Line 211: `test_role` → should be `test_model_role`
- Line 232: `test_user` → should be `test_model_user`
- Line 232: `test_role` → should be `test_model_role`
- Line 253: `test_group` → should be `test_model_group`
- Line 253: `test_user` → should be `test_model_user`
- Line 355: `test_role` → should be `test_model_role`

## Implementation Plan

### Phase 1: Identify Available Fixtures

**Objective**: Verify which fixtures actually exist and their correct names

```bash
# List all available fixtures
uv run pytest --fixtures | grep -E "test_model|test_schema"
```

**Expected Available Fixtures**:
- `test_model_user`
- `test_model_questions` 
- `test_model_answer_choices`
- `test_model_group`
- `test_model_role`
- `test_model_subject`
- `test_model_topic`
- `test_model_subtopic`
- `test_model_concept`

### Phase 2: Update Fixture References

**Target File**: `backend/tests/integration/api/test_database_error_handling.py`

**Method**: Systematic find-and-replace with verification

```python
# Pattern replacements needed:
FIXTURE_MAPPINGS = {
    "test_questions": "test_model_questions",
    "test_user": "test_model_user", 
    "test_answer_choices": "test_model_answer_choices",
    "test_group": "test_model_group",
    "test_role": "test_model_role",
    "test_subject": "test_model_subject",
    "test_topic": "test_model_topic",
    "test_subtopic": "test_model_subtopic",
    "test_concept": "test_model_concept"
}
```

**Example Changes**:

```python
# Before
def test_user_response_creation_with_invalid_user_id(logged_in_client, test_questions, test_answer_choices):

# After  
def test_user_response_creation_with_invalid_user_id(logged_in_client, test_model_questions, test_model_answer_choices):
```

```python
# Before
"question_id": test_questions[0].id,
"answer_choice_id": test_answer_choices[0].id,

# After
"question_id": test_model_questions[0].id, 
"answer_choice_id": test_model_answer_choices[0].id,
```

### Phase 3: Verify Fixture Compatibility

**Objective**: Ensure the renamed fixtures provide the expected data structure

**Test File Structure Verification**:

```python
def test_fixture_data_structure(test_model_questions, test_model_answer_choices, test_model_user):
    """Verify that fixtures provide expected data structure."""
    
    # test_model_questions should be a list
    assert isinstance(test_model_questions, list)
    assert len(test_model_questions) > 0
    
    # Each question should have an id
    for question in test_model_questions:
        assert hasattr(question, 'id')
        assert question.id is not None
    
    # test_model_answer_choices should be a list
    assert isinstance(test_model_answer_choices, list)
    assert len(test_model_answer_choices) > 0
    
    # Each answer choice should have an id
    for choice in test_model_answer_choices:
        assert hasattr(choice, 'id')
        assert choice.id is not None
    
    # test_model_user should be a single object
    assert hasattr(test_model_user, 'id')
    assert test_model_user.id is not None
```

### Phase 4: Handle Scope Mismatches

**Potential Issue**: Some fixtures may have different scopes (function vs session)

**Investigation Required**:

```python
# Check fixture definitions in fixture files
# Look for scope mismatches that could cause issues

@pytest.fixture(scope="function")  # vs @pytest.fixture(scope="session")
def test_model_user(...):
    ...
```

**Resolution Strategy**:
- Document any scope differences
- Adjust test expectations if needed
- Ensure compatibility with test isolation requirements

## Dependencies

**Can Run Independently**: This task addresses immediate fixture reference errors and doesn't depend on database infrastructure changes.

**Provides For**:
- **Task 4**: Some constraint tests may work once fixture references are fixed
- **General Testing**: Removes immediate blockers for test execution

**May Reveal**: After fixing fixture names, some tests may still fail due to infrastructure issues (Tasks 2-3), but failures will be more meaningful.

## Verification Steps

### Step 1: Fixture Availability Check

```bash
# Verify all required fixtures exist
uv run pytest --fixtures backend/tests/integration/api/test_database_error_handling.py | grep -E "test_model"
```

### Step 2: Syntax Verification

```bash
# Check that Python syntax is correct after changes
python -m py_compile backend/tests/integration/api/test_database_error_handling.py
```

### Step 3: Test Discovery

```bash
# Verify pytest can discover and collect tests
uv run pytest --collect-only backend/tests/integration/api/test_database_error_handling.py
```

### Step 4: Fixture Injection Test

```bash
# Run a simple test to verify fixtures are properly injected
uv run pytest -v backend/tests/integration/api/test_database_error_handling.py::test_user_creation_with_invalid_role_id -s
```

## Success Criteria

- [x] **No Missing Fixture Errors**: All fixture references resolve successfully
- [x] **Consistent Naming**: All fixture references follow `test_model_*` convention
- [x] **Test Discovery**: Pytest can collect all tests without import errors
- [x] **Fixture Injection**: Fixtures are properly injected into test functions
- [x] **Data Structure Compatibility**: Fixtures provide expected data types and attributes
- [x] **No Regression**: Existing passing tests continue to pass
- [x] **Clear Error Messages**: Remaining test failures show real issues, not fixture problems

## Risk Assessment

### Low Risk Changes
- **Simple Renaming**: Straightforward find-and-replace operations
- **No Logic Changes**: Only changing fixture parameter names

### Potential Issues
- **Fixture Data Structure**: New fixtures might have different data structure than expected
- **Scope Mismatches**: Function vs session scope fixtures might cause issues
- **Missing Fixtures**: Some referenced fixtures might not exist yet

### Mitigation Strategies
1. **Incremental Changes**: Update one test function at a time
2. **Structure Verification**: Test fixture data structure before making all changes
3. **Rollback Plan**: Keep track of changes for easy rollback if issues arise

## Implementation Notes

### Change Tracking
Document all fixture name changes for future reference:

```markdown
## Fixture Name Mapping
| Old Name | New Name | Status |
|----------|----------|---------|
| test_questions | test_model_questions | ✅ Updated |
| test_user | test_model_user | ✅ Updated |
| test_answer_choices | test_model_answer_choices | ✅ Updated |
| test_group | test_model_group | ✅ Updated |
| test_role | test_model_role | ✅ Updated |
```

### Future Prevention
- Update documentation to clarify current fixture naming convention
- Consider adding linting rules to catch fixture naming inconsistencies
- Document available fixtures for test authors

---

**Dependencies**: None (can run independently)  
**Impacts**: Tasks 2-4 (may reduce some test failures)  
**Estimated Timeline**: 1-2 hours for systematic updates and verification  
**Assigned To**: Development Team  
**Priority**: Medium (unblocks immediate test execution issues)