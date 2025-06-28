# Quiz App Test Suite

This directory contains tests for the Quiz Application backend. The test suite follows the "Real Objects Testing Philosophy," emphasizing integration testing with real components while maintaining proper layer isolation.

## Directory Structure (Aspirational)

The following structure represents the intended organization for proper test categorization:

```tree
backend/tests/
├── conftest.py             # Pytest configuration and shared fixtures
├── fixtures/               # Test fixtures for creating test instances
│   ├── models/             # SQLAlchemy model fixtures
│   ├── crud/               # CRUD operation fixtures
│   ├── api/                # API endpoint fixtures
│   └── services/           # Service layer fixtures
├── helpers/                # Helper modules for testing
│   ├── factories/          # Factory functions for creating test data
│   ├── assertions/         # Custom assertion helpers
│   └── database/           # Database testing utilities
├── unit/                   # Tests for single-component isolation
│   ├── models/             # SQLAlchemy model tests (business logic only)
│   ├── schemas/            # Pydantic schema validation tests
│   ├── services/           # Service layer business logic tests
│   └── utils/              # Utility function tests
└── integration/            # Tests for cross-component interactions
    ├── crud/               # Database operation integration tests
    ├── api/                # API endpoint integration tests
    └── workflows/          # End-to-end workflow tests
```

### Current Structure

✅ **Fully Implemented**: The test suite now follows proper unit/integration separation:

```tree
backend/tests/
├── conftest.py             # Pytest configuration and shared fixtures
├── fixtures/               # Test fixtures for creating test instances
│   ├── models/             # SQLAlchemy model fixtures
│   ├── schemas/            # Pydantic schema fixtures
│   ├── api/                # API endpoint fixtures
│   ├── database/           # Database testing utilities
│   └── integration/        # Complex integration fixtures
├── helpers/                # Helper modules for testing
│   ├── factories/          # Factory functions for creating test data
│   ├── assertions/         # Custom assertion helpers
│   └── database/           # Database testing utilities
├── unit/                   # Tests for single-component isolation
│   ├── models/             # SQLAlchemy model business logic tests
│   ├── schemas/            # Pydantic schema validation tests
│   ├── services/           # Service layer business logic tests
│   └── utils/              # Utility function tests
└── integration/            # Tests for cross-component interactions
    ├── crud/               # Database operation integration tests
    ├── api/                # API endpoint integration tests
    ├── models/             # Model database interaction tests
    ├── services/           # Service database integration tests
    ├── database/           # Database session and connection tests
    └── workflows/          # End-to-end workflow tests
```

## Test Types

Quiz App follows proper test categorization with two main types of tests:

### Unit Tests

Unit tests focus on a single component in isolation:

- **Models**: Testing model properties, methods, and business logic (no database)
- **Schemas**: Testing Pydantic schema validation and serialization
- **Services**: Testing business logic methods without external dependencies
- **Utils**: Testing utility functions

Example unit test:

```python
def test_question_schema_validation():
    """Test validation in QuestionCreateSchema."""
    # Valid data should pass validation
    valid_data = {
        "text": "What is the capital of France?",
        "difficulty": "Beginner",
        "subject_ids": [1, 2],
        "topic_ids": [1],
        "subtopic_ids": [1],
        "concept_ids": [1]
    }
    schema = QuestionCreateSchema(**valid_data)
    assert schema.text == "What is the capital of France?"
    assert schema.difficulty == "Beginner"
    
    # Invalid data should fail validation
    with pytest.raises(ValidationError):
        QuestionCreateSchema(text="", difficulty="Beginner")  # Empty text
```

### Integration Tests

Integration tests focus on components that span multiple layers:

- **CRUD Operations**: Testing database interactions with real database connections
- **API Endpoints**: Testing full request/response cycles through FastAPI
- **Services**: Testing business logic that integrates with databases and external systems
- **Workflows**: Testing complete user workflows across multiple components

Example integration test:

```python
def test_create_question_with_answers(db_session, test_subject, test_user):
    """Test creating a question with answer choices through CRUD layer."""
    from backend.app.models.questions import DifficultyLevel
    from backend.app.crud.crud_questions import create_question_in_db
    from backend.app.crud.crud_answer_choices import create_answer_choice_in_db
    
    # Create test question data
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "creator_id": test_user.id
    }
    
    # Create question through CRUD
    question = create_question_in_db(db_session, question_data)
    
    # Create answer choices
    answer_choices = [
        {"text": "Paris", "is_correct": True, "question_id": question.id},
        {"text": "London", "is_correct": False, "question_id": question.id},
        {"text": "Berlin", "is_correct": False, "question_id": question.id}
    ]
    
    created_answers = []
    for choice_data in answer_choices:
        answer = create_answer_choice_in_db(db_session, choice_data)
        created_answers.append(answer)
    
    # Verify question was created with relationships
    assert question.text == "What is the capital of France?"
    assert question.difficulty == DifficultyLevel.EASY
    assert len(created_answers) == 3
    assert sum(1 for a in created_answers if a.is_correct) == 1
```

## Testing Philosophy

Quiz App follows these core testing principles:

1. **No Mocks Policy**: We strictly prohibit using unittest.mock, MagicMock, or any mocking libraries - mocks are brittle and cause more headaches than they're worth
2. **Real Database Testing**: Integration tests use a real test database that gets set up/torn down between tests
3. **Proper Test Separation**: Unit tests focus on single components, integration tests verify cross-layer interactions
4. **Real Objects**: All test data uses real SQLAlchemy models and Pydantic schemas
5. **Function-Style Tests**: All tests are written as functions, not classes
6. **Consistent Data**: All test data follows the same validation rules as production data

## Test Organization Guidelines

### Unit Test Guidelines

- Test single components in isolation
- No database connections (use in-memory objects)
- No external API calls
- Fast execution (< 1ms per test)
- Focus on business logic and validation

### Integration Test Guidelines

- Test interactions between multiple components
- Use real database connections (test database)
- Test complete workflows and user scenarios
- Slower execution acceptable (< 1s per test)
- Focus on data flow and system behavior

### Fixture Guidelines

- Create reusable test data factories
- Use database fixtures for integration tests
- Use in-memory fixtures for unit tests
- Register all fixtures in conftest.py
- Follow naming convention: `test_<component>_<description>`

### Test Migration Status

✅ **Completed**: The test suite has been successfully reorganized to follow proper unit/integration separation. All tests are now properly categorized according to their scope and dependencies.
