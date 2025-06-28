# Test Refactoring Task 6: Model Integration Tests

## Objective
Move existing model tests (which are actually integration tests) to the `integration/models/` directory, since they test database interactions, relationships, and persistence rather than pure business logic.

## Background
The current `test_models/` directory contains tests that use database sessions and test model persistence, relationships, and database constraints. After Task 3 extracts the unit tests, these remaining tests are proper integration tests that validate database interactions.

## Current Model Test Files
Based on directory listing, we have model tests for:
- `test_answer_choice_model.py`
- `test_associations.py`
- `test_concept_model.py`
- `test_group_model.py`
- `test_question_model.py` ✅ Already reviewed - mostly integration tests
- `test_question_set_model.py`
- `test_question_tag_model.py`
- `test_role_model.py`
- `test_subject_model.py`
- `test_subtopic_model.py`
- `test_topic_model.py`
- `test_user_model.py` ✅ Already reviewed - mostly integration tests
- `test_user_response_model.py`

## Analysis of Current Model Tests
From review of `test_question_model.py`, current tests focus on:
- Database creation and persistence ✅ Integration tests
- SQLAlchemy relationship testing ✅ Integration tests
- Foreign key constraint validation ✅ Integration tests
- Many-to-many association testing ✅ Integration tests
- Database transaction and rollback testing ✅ Integration tests

## Task Details

### 1. Verify Model Tests Are Database Integration Tests
Before migration, verify that model tests use database features:

```bash
# Check for database session usage
grep -r "db_session\|commit\|flush\|refresh" backend/tests/test_models/ | head -10

# Check for relationship testing
grep -r "relationship\|append\|association\|foreign" backend/tests/test_models/ | head -10

# Check for database constraint testing
grep -r "IntegrityError\|unique\|constraint" backend/tests/test_models/ | head -5
```

### 2. Move Model Tests to Integration Directory
Move each model test file to the new integration structure:

```bash
# Move model tests to integration directory
mv backend/tests/test_models/test_answer_choice_model.py backend/tests/integration/models/test_answer_choice_model.py
mv backend/tests/test_models/test_associations.py backend/tests/integration/models/test_associations.py
mv backend/tests/test_models/test_concept_model.py backend/tests/integration/models/test_concept_model.py
mv backend/tests/test_models/test_group_model.py backend/tests/integration/models/test_group_model.py
mv backend/tests/test_models/test_question_model.py backend/tests/integration/models/test_question_model.py
mv backend/tests/test_models/test_question_set_model.py backend/tests/integration/models/test_question_set_model.py
mv backend/tests/test_models/test_question_tag_model.py backend/tests/integration/models/test_question_tag_model.py
mv backend/tests/test_models/test_role_model.py backend/tests/integration/models/test_role_model.py
mv backend/tests/test_models/test_subject_model.py backend/tests/integration/models/test_subject_model.py
mv backend/tests/test_models/test_subtopic_model.py backend/tests/integration/models/test_subtopic_model.py
mv backend/tests/test_models/test_topic_model.py backend/tests/integration/models/test_topic_model.py
mv backend/tests/test_models/test_user_model.py backend/tests/integration/models/test_user_model.py
mv backend/tests/test_models/test_user_response_model.py backend/tests/integration/models/test_user_response_model.py
```

### 3. Update File Names for Clarity
Since these are now clearly in the `integration/models/` directory, consider cleaner names:
- Keep existing names but verify they clearly indicate integration nature
- Files should follow pattern: `test_{model}_model.py` or `test_{concept}.py`

### 4. Verify Database Integration Test Characteristics
Ensure moved tests demonstrate proper database integration patterns:

#### Example Database Integration Test Pattern
```python
def test_question_model_creation(db_session):
    """Test QuestionModel database creation and persistence."""
    question = QuestionModel(
        text="What is the capital of France?", 
        difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.commit()

    # Verify database persistence
    assert question.id is not None
    assert question.text == "What is the capital of France?"
    assert question.difficulty == DifficultyLevel.EASY
    
    # Verify retrieval from database
    retrieved = db_session.query(QuestionModel).filter_by(id=question.id).first()
    assert retrieved is not None
    assert retrieved.text == question.text

def test_question_relationships(db_session, test_model_subject):
    """Test QuestionModel database relationships."""
    question = QuestionModel(
        text="Test question", 
        difficulty=DifficultyLevel.EASY
    )
    question.subjects.append(test_model_subject)
    db_session.add(question)
    db_session.commit()

    # Verify relationship persistence in database
    db_session.refresh(question)
    assert test_model_subject in question.subjects
    assert question in test_model_subject.questions
    
    # Verify through fresh database query
    fresh_question = db_session.query(QuestionModel).filter_by(id=question.id).first()
    assert len(fresh_question.subjects) == 1
    assert fresh_question.subjects[0].id == test_model_subject.id
```

### 5. Identify Association Table Tests
The `test_associations.py` file likely tests many-to-many relationships:

#### Example Association Test Pattern
```python
def test_question_to_answer_association(db_session):
    """Test many-to-many relationship between questions and answers."""
    question = QuestionModel(text="Test", difficulty=DifficultyLevel.EASY)
    answer = AnswerChoiceModel(text="Answer", is_correct=True)
    
    # Test association creation
    question.answer_choices.append(answer)
    db_session.add(question)
    db_session.add(answer)
    db_session.commit()
    
    # Verify association in database
    assert answer in question.answer_choices
    assert question in answer.questions
    
    # Test association deletion
    question.answer_choices.remove(answer)
    db_session.commit()
    
    # Verify association removed but entities remain
    assert answer not in question.answer_choices
    assert db_session.query(AnswerChoiceModel).filter_by(id=answer.id).first() is not None
```

### 6. Update Any Import References
Check if any other test files import from the old model test locations:
```bash
grep -r "from.*test_models" backend/tests/
grep -r "import.*test_models" backend/tests/
```

### 7. Remove Empty Directory
After migration, remove the old `test_models/` directory:
```bash
rmdir backend/tests/test_models/
```

## Testing Strategy

### Verify Model Integration Tests Work in New Location
```bash
# Run only the migrated model integration tests
uv run pytest backend/tests/integration/models/ -v

# Verify they use database properly (slower execution expected)
time uv run pytest backend/tests/integration/models/ -v

# Check for proper database integration patterns
uv run pytest backend/tests/integration/models/test_question_model.py -v -s
```

### Test Database Relationships
```bash
# Verify relationship tests work
uv run pytest backend/tests/integration/models/test_associations.py -v
uv run pytest backend/tests/integration/models/ -k "relationship" -v
```

### Test Database Constraints
```bash
# Test database constraint validation
uv run pytest backend/tests/integration/models/ -k "unique\|constraint" -v
```

### Run Full Test Suite
```bash
# Ensure overall test suite still works
uv run pytest backend/tests/ -v --tb=short
```

## Success Criteria
- [ ] All model tests moved to `backend/tests/integration/models/`
- [ ] File names maintained or cleaned up appropriately
- [ ] All moved tests pass in new location
- [ ] Tests demonstrate proper database integration patterns
- [ ] Database relationships and constraints tested
- [ ] Association table tests working
- [ ] Old `test_models/` directory removed
- [ ] Full test suite still passes
- [ ] Tests properly use database fixtures and sessions

## Implementation Notes
- Model tests are already integration tests - minimal changes needed
- Focus on moving rather than rewriting
- Preserve all existing database test logic and assertions
- Ensure pytest discovery works with new file paths
- Validate that database fixtures still work correctly in new location
- Maintain test isolation between database tests

## Database Integration Test Characteristics to Verify
1. **Database Sessions**: All tests should use `db_session` fixture
2. **Data Persistence**: Tests should verify data survives database commits
3. **Relationship Testing**: Tests should validate SQLAlchemy relationships
4. **Constraint Validation**: Tests should test database constraints (unique, foreign key)
5. **Transaction Handling**: Tests should properly manage database transactions
6. **Association Tables**: Tests should validate many-to-many relationships
7. **Cascade Behavior**: Tests should verify deletion cascades

## Common Issues to Watch For
1. **Fixture Dependencies**: Ensure model fixtures work in new location
2. **Database State**: Verify test cleanup doesn't affect other tests
3. **Foreign Key Order**: Ensure test data creation order respects constraints
4. **Session Management**: Verify session commit/rollback behavior
5. **Relationship Loading**: Ensure lazy/eager loading works as expected
6. **Constraint Testing**: Verify integrity error testing still works

## Distinction from Unit Tests
These integration tests should be clearly different from the unit tests created in Task 3:

| Unit Tests (Task 3) | Integration Tests (Task 6) |
|---------------------|----------------------------|
| No database | Uses database sessions |
| In-memory objects | Persistent database objects |
| Business logic only | Database interactions |
| Fast execution | Slower execution |
| No relationships | Tests relationships |
| `unit/models/` | `integration/models/` |

## Next Task
After completion, move to `test_refactoring_7_service_test_separation.md` to separate service tests into unit and integration categories.

## Testing Commands
```bash
# Quick verification commands
find backend/tests/integration/models/ -name "*.py" | wc -l  # Should show 13 files
uv run pytest backend/tests/integration/models/test_question_model.py -v  # Test one specific file
uv run pytest backend/tests/integration/ -v  # Test all integration tests so far
grep -r "db_session" backend/tests/integration/models/ | wc -l  # Should show many database usages
```