# Test Refactoring Task 3: Model Unit Tests

## Objective
Extract pure business logic from current model tests to create true unit tests that test model methods, properties, and validation without database dependencies.

## Background
Current model tests in `test_models/` are actually integration tests because they use `db_session` and test database relationships. We need to separate the business logic testing (unit tests) from the database interaction testing (integration tests).

## Analysis of Current Model Tests
Based on review of files like `test_question_model.py` and `test_user_model.py`, current tests focus on:
- Database creation and persistence ➡️ Integration tests
- Relationship validation ➡️ Integration tests  
- Model `__repr__` methods ➡️ Unit tests
- Property validation ➡️ Unit tests
- Business logic methods ➡️ Unit tests

## Current Model Files to Extract From
- `test_answer_choice_model.py`
- `test_associations.py` 
- `test_concept_model.py`
- `test_group_model.py`
- `test_question_model.py` ✅ Already reviewed
- `test_question_set_model.py`
- `test_question_tag_model.py`
- `test_role_model.py`
- `test_subject_model.py`
- `test_subtopic_model.py`
- `test_topic_model.py`
- `test_user_model.py` ✅ Already reviewed
- `test_user_response_model.py`

## Task Details

### 1. Analyze Model Classes for Business Logic
First, identify what business logic exists in each model that can be unit tested:

**Example Analysis for UserModel:**
```python
# From backend/app/models/users.py
class UserModel(Base):
    # Properties that can be unit tested:
    def __repr__(self):  # ✅ Unit testable
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role_id='{self.role_id}')>"
    
    # Default values that can be unit tested:
    is_active = Column(Boolean, default=True)  # ✅ Unit testable
    is_admin = Column(Boolean, default=False)  # ✅ Unit testable
```

### 2. Create Unit Tests for Model Business Logic
For each model, create unit tests that focus on:

#### UserModel Unit Tests (`backend/tests/unit/models/test_user.py`)
```python
import pytest
from backend.app.models.users import UserModel

def test_user_model_repr():
    """Test UserModel string representation."""
    user = UserModel(
        id=1,
        username="testuser", 
        email="test@example.com",
        role_id=2
    )
    expected = "<User(id=1, username='testuser', email='test@example.com', role_id='2')>"
    assert repr(user) == expected

def test_user_model_defaults():
    """Test UserModel default values."""
    user = UserModel(username="test", email="test@example.com", hashed_password="hash")
    assert user.is_active is True
    assert user.is_admin is False
```

#### QuestionModel Unit Tests (`backend/tests/unit/models/test_question.py`)
```python
import pytest
from backend.app.models.questions import QuestionModel, DifficultyLevel

def test_question_model_repr():
    """Test QuestionModel string representation.""" 
    question = QuestionModel(
        id=1,
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    expected = "<QuestionModel(id=1, text='What is the capital of France?...', difficulty='DifficultyLevel.EASY')>"
    assert repr(question) == expected

def test_question_difficulty_enum():
    """Test DifficultyLevel enum usage in QuestionModel."""
    question = QuestionModel(text="Test", difficulty=DifficultyLevel.MEDIUM)
    assert question.difficulty == DifficultyLevel.MEDIUM
    assert question.difficulty.value == "Medium"
```

### 3. Identify What Stays as Integration Tests
Keep these test patterns as integration tests (will be moved in Task 6):
- Tests using `db_session` fixture
- Database relationship testing
- Database constraint testing (unique, foreign key)
- CRUD operations through the database
- Association table testing

### 4. Create Unit Test Files
Create new unit test files following the pattern:
- `backend/tests/unit/models/test_answer_choice.py`
- `backend/tests/unit/models/test_concept.py` 
- `backend/tests/unit/models/test_group.py`
- `backend/tests/unit/models/test_question.py`
- `backend/tests/unit/models/test_question_set.py`
- `backend/tests/unit/models/test_question_tag.py`
- `backend/tests/unit/models/test_role.py`
- `backend/tests/unit/models/test_subject.py`
- `backend/tests/unit/models/test_subtopic.py`
- `backend/tests/unit/models/test_topic.py`
- `backend/tests/unit/models/test_user.py`
- `backend/tests/unit/models/test_user_response.py`

### 5. Extract Unit-Testable Code Patterns

#### Pattern 1: Model Representation Methods
```python
def test_model_repr():
    """Test model string representation without database."""
    model = ModelClass(field1="value1", field2="value2")
    expected_repr = f"<ModelClass(field1='value1', field2='value2')>"
    assert repr(model) == expected_repr
```

#### Pattern 2: Default Values and Properties  
```python
def test_model_defaults():
    """Test model default values."""
    model = ModelClass(required_field="value")
    assert model.optional_field == expected_default
    assert model.boolean_field is True
```

#### Pattern 3: Enum and Validation Logic
```python
def test_model_enum_handling():
    """Test enum field handling."""
    model = ModelClass(enum_field=EnumType.VALUE)
    assert model.enum_field == EnumType.VALUE
    assert model.enum_field.value == "expected_string"
```

#### Pattern 4: Computed Properties (if any)
```python
def test_model_computed_property():
    """Test computed properties without database."""
    model = ModelClass(field1="value1", field2="value2")
    assert model.computed_property == "expected_result"
```

## Testing Strategy

### Verify Unit Tests Are Database-Free
```bash
# Check that new unit tests don't use database fixtures
grep -r "db_session\|Session" backend/tests/unit/models/ || echo "No database dependencies found"

# Verify unit tests run quickly
time uv run pytest backend/tests/unit/models/ -v
```

### Run New Unit Tests
```bash
# Test individual model unit tests
uv run pytest backend/tests/unit/models/test_user.py -v
uv run pytest backend/tests/unit/models/test_question.py -v

# Test all model unit tests
uv run pytest backend/tests/unit/models/ -v

# Verify they're fast
time uv run pytest backend/tests/unit/models/ -v
```

## Success Criteria
- [ ] Unit test files created for all 12 model types
- [ ] Each unit test focuses on business logic only (no database)
- [ ] All `__repr__` methods tested
- [ ] Default values and properties tested  
- [ ] Enum handling tested where applicable
- [ ] Unit tests run quickly (< 2 seconds total)
- [ ] No database fixtures or sessions in unit tests
- [ ] Original integration tests preserved for Task 6

## Implementation Notes
- **Start Small**: Begin with models that have clear business logic (User, Question)
- **No Database**: Unit tests should create models in memory only
- **Focus on Logic**: Test methods, properties, and validation rules
- **Preserve Original**: Don't modify existing integration tests yet
- **Clear Separation**: Unit tests should be clearly distinguishable from integration tests

## Expected Challenges
1. **Limited Business Logic**: Some models may have minimal unit-testable logic
2. **Enum Imports**: Ensure proper imports for enums and constants
3. **Fixture Dependencies**: Unit tests should not depend on database fixtures
4. **Model Dependencies**: Some models may require other models - use minimal in-memory instances

## Next Task  
After completion, move to `test_refactoring_4_crud_integration_tests.md` to properly organize the CRUD layer integration tests.

## Testing Commands
```bash
# Quick verification
find backend/tests/unit/models/ -name "*.py" | wc -l  # Should show 12+ files
uv run pytest backend/tests/unit/ -v  # All unit tests so far
python -c "from backend.app.models.users import UserModel; u=UserModel(username='test', email='test@test.com', hashed_password='hash'); print(repr(u))"  # Test model creation
```