# Test Refactoring Task 1: Create Foundation

## Objective
Create the foundation for test suite refactoring by establishing proper directory structure according to the standards in `backend/tests/CLAUDE.md`.

## Background
The current test suite mixes unit and integration test concerns. Per the aspirational structure in `CLAUDE.md`, we need to reorganize tests into proper `unit/` and `integration/` directories with clear separation of concerns.

## Current State
Tests are organized by component type:
- `test_models/` - Mixed unit/integration model tests (uses db_session)
- `test_schemas/` - Pure unit tests (no external dependencies) ✅ 
- `test_api/` - Integration tests through FastAPI
- `test_crud/` - Integration tests with database
- `test_services/` - Mixed business logic and database tests
- `test_core/` - Core functionality tests
- `test_db/` - Database session tests
- `test_integration/` - Cross-system integration tests

## Task Details

### 1. Create New Directory Structure
Create the aspirational directory structure as defined in `CLAUDE.md`:

```bash
# Create unit test directories
mkdir -p backend/tests/unit/models
mkdir -p backend/tests/unit/schemas  
mkdir -p backend/tests/unit/services
mkdir -p backend/tests/unit/utils

# Create integration test directories
mkdir -p backend/tests/integration/crud
mkdir -p backend/tests/integration/api
mkdir -p backend/tests/integration/models
mkdir -p backend/tests/integration/services
mkdir -p backend/tests/integration/workflows

# Create helper directories
mkdir -p backend/tests/helpers/factories
mkdir -p backend/tests/helpers/assertions
mkdir -p backend/tests/helpers/database
```

### 2. Create __init__.py Files
Add `__init__.py` files to maintain Python package structure:

```bash
touch backend/tests/unit/__init__.py
touch backend/tests/unit/models/__init__.py
touch backend/tests/unit/schemas/__init__.py
touch backend/tests/unit/services/__init__.py
touch backend/tests/unit/utils/__init__.py

touch backend/tests/integration/__init__.py
touch backend/tests/integration/crud/__init__.py
touch backend/tests/integration/api/__init__.py
touch backend/tests/integration/models/__init__.py
touch backend/tests/integration/services/__init__.py
touch backend/tests/integration/workflows/__init__.py

touch backend/tests/helpers/__init__.py
touch backend/tests/helpers/factories/__init__.py
touch backend/tests/helpers/assertions/__init__.py
touch backend/tests/helpers/database/__init__.py
```

### 3. Verify Current Test Suite Still Works
Before making any moves, verify the current test suite runs successfully:

```bash
uv run pytest backend/tests/ -v
```

Record any current test failures to ensure we don't introduce new issues.

## Success Criteria
- [ ] New directory structure created according to `CLAUDE.md` specification
- [ ] All new directories have proper `__init__.py` files
- [ ] Current test suite still runs without new failures
- [ ] Git tracking includes new directories (add a placeholder file if needed)

## Implementation Notes
- This task only creates structure, no tests are moved yet
- Preserve existing test structure until migration tasks
- Ensure pytest can discover the new directory structure
- Follow Python package conventions with `__init__.py` files

## Next Task
After completion, move to `test_refactoring_2_schema_unit_tests.md` to migrate schema tests as the first validation of the new structure.

## Testing Commands
```bash
# Verify directory structure
find backend/tests/unit backend/tests/integration backend/tests/helpers -name "*.py" | head -20

# Run current tests to establish baseline
uv run pytest backend/tests/ -v --tb=short

# Check new directories are Python packages
python -c "import backend.tests.unit; import backend.tests.integration; print('Package structure OK')"
```