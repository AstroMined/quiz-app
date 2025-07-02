# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Quiz Application is a Python-based educational platform for creating, managing, and delivering interactive quizzes. The application provides comprehensive quiz management with user authentication, question categorization, and performance tracking. The project has two main components:

- **Backend** (`/backend`): FastAPI-based REST API with SQLAlchemy models and comprehensive test coverage
- **Frontend** (`/frontend`): Next.js/React application (currently non-functional, planned for rebuild)

## Architecture Overview

The backend follows a layered architecture:

1. **Database Layer** (`backend/app/db/`): SQLAlchemy models and session management
2. **CRUD Layer** (`backend/app/crud/`): Data access operations with specialized implementations
3. **Schema Layer** (`backend/app/schemas/`): Pydantic schemas for validation and serialization
4. **Service Layer** (`backend/app/services/`): Business logic services
5. **API Layer** (`backend/app/api/endpoints/`): FastAPI endpoints with comprehensive routing
6. **Middleware Layer** (`backend/app/middleware/`): Authentication, authorization, and CORS handling

Key architectural patterns:

- **Layered Architecture**: Clear separation of concerns across database, business logic, and API layers
- **CRUD Pattern**: Centralized data access operations with consistent interfaces
- **Schema Validation**: Pydantic models for request/response validation and serialization
- **Service Layer**: Business logic abstraction with dependency injection

## Development Commands

### Environment Setup

```bash
# UV-based environment with Python 3.12 (recommended)
uv sync --all-extras  # Install all dependencies including dev tools

# For development with auto-reload
uv sync --dev  # Install only dev dependencies if needed

# Python version: 3.12.10 (managed by UV)
```

### Running the Application

```bash
# Backend development server (from project root)
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development server (when functional)
cd frontend
npm run dev

# Run with database initialization
uv run python -m backend.app.main
```

### Testing

```bash
# Run all tests with UV (parallel execution for better performance)
uv run pytest -n auto

# Run tests with specific number of workers
uv run pytest -n 4

# Run tests in serial mode (if needed for debugging)
uv run pytest

# Run with coverage
uv run pytest --cov=backend/

# Run specific test categories
uv run pytest backend/tests/unit/ -n auto
uv run pytest backend/tests/integration/ -n auto
uv run pytest backend/tests/performance/ -n auto

# Run performance tests only (may take longer)
uv run pytest backend/tests/performance/ -v

# Run tests by marker
uv run pytest -m unit -n auto
uv run pytest -m integration -n auto
uv run pytest -m performance

# Run single test file
uv run pytest backend/tests/test_models/test_question_model.py

# Run with verbose output
uv run pytest -v -n auto

# Performance comparison
time uv run pytest -n 1  # Serial execution
time uv run pytest -n auto  # Parallel execution
```

### Code Quality

```bash
# Format code
uv run black backend/

# Sort imports  
uv run isort backend/

# Static analysis
uv run pylint backend/

# Type checking (mypy not installed by default)
uv add --dev mypy
uv run mypy backend/
```

### Database Management

```bash
# Database migrations (Alembic)
alembic upgrade head
alembic revision --autogenerate -m "Description"

# Database files (SQLite)
# Development: backend/db/quiz_app.db
# Testing: backend/db/test.db

# Reset development database (recreate from scratch)
rm backend/db/quiz_app.db
alembic upgrade head
```

## Key Components

### Database Models (`backend/app/models/`)

- **Core Models**: `base.py` - Base model with common fields and audit functionality
- **User Management**: `users.py`, `authentication.py`, `permissions.py`, `roles.py` - User system and access control
- **Quiz Structure**: `questions.py`, `answer_choices.py`, `question_sets.py`, `question_tags.py` - Core quiz functionality
- **Content Organization**: `subjects.py`, `topics.py`, `subtopics.py`, `concepts.py`, `disciplines.py`, `domains.py` - Content categorization
- **User Interaction**: `user_responses.py`, `leaderboard.py`, `groups.py` - User engagement and scoring
- **Associations**: `associations.py` - Many-to-many relationship tables

### CRUD Layer (`backend/app/crud/`)

- **Authentication**: `authentication.py` - User authentication and session management
- **User Management**: `crud_user.py`, `crud_permissions.py`, `crud_roles.py` - User system operations
- **Quiz Management**: `crud_questions.py`, `crud_answer_choices.py`, `crud_question_sets.py`, `crud_question_tags.py` - Core quiz operations
- **Content Management**: `crud_subjects.py`, `crud_topics.py`, `crud_subtopics.py`, `crud_concepts.py` - Content organization
- **Response Tracking**: `crud_user_responses.py`, `crud_leaderboard.py` - User interaction tracking

### Schema Validation (`backend/app/schemas/`)

- **Pydantic Schemas**: Request/response validation and serialization for all models
- **Custom Validators**: Quiz-specific validation logic (difficulty levels, question formats, etc.)
- **Authentication Schemas**: `authentication.py`, `user.py` - User authentication and profile schemas
- **Quiz Schemas**: `questions.py`, `answer_choices.py`, `question_sets.py` - Core quiz data validation
- **Content Schemas**: `subjects.py`, `topics.py`, `concepts.py` - Content organization schemas

### Testing Structure

- **Unit Tests**: `backend/tests/unit/` - Single-component isolation testing
  - `models/` - SQLAlchemy model tests (business logic only)
  - `schemas/` - Pydantic schema validation tests
  - `services/` - Service layer business logic tests
  - `utils/` - Utility function tests
- **Integration Tests**: `backend/tests/integration/` - Cross-component testing
  - `crud/` - Database operation tests
  - `api/` - API endpoint tests
  - `services/` - Service database integration tests
  - `workflows/` - End-to-end workflow tests
- **Performance Tests**: `backend/tests/performance/` - Performance benchmarks and monitoring
  - `test_performance_benchmarks.py` - Performance measurement tests
  - `test_performance_monitoring.py` - Performance regression detection
  - `test_fixture_performance.py` - Fixture performance optimization
- **Fixtures**: `backend/tests/fixtures/` - Reusable test data creation
- **Helpers**: `backend/tests/helpers/` - Test utility functions

## Domain Model

### Quiz Content Structure

- **Questions**: Core quiz questions with difficulty levels, text content, and metadata
- **Answer Choices**: Multiple choice options with correct/incorrect marking
- **Question Sets**: Grouped collections of questions for organized quiz delivery
- **Content Hierarchy**: Subjects → Topics → Subtopics → Concepts for detailed categorization

### User Management

- **User Accounts**: Authentication, profiles, and role-based permissions
- **Groups**: User organization for collaborative learning
- **Responses**: User answer tracking with scoring and timing
- **Leaderboards**: Performance tracking and competitive elements

## Documentation Maintenance

### Documentation Update Protocol

When working in any directory, follow this protocol to maintain documentation accuracy:

1. **Read First**: Always read the existing CLAUDE.md file before starting work
2. **Verify Examples**: Check that documented examples match your current implementation
3. **Update Patterns**: If architectural patterns have changed, update documentation immediately
4. **Add New Patterns**: Document any new patterns you introduce with clear examples
5. **Test Examples**: Ensure documented code examples actually work as written
6. **Fix on Discovery**: If you notice outdated guidance, fix it as part of your current task

### When Documentation Updates Are Required

- ✅ **Always Required**:
  - New public methods or changed interfaces
  - New architectural patterns or design decisions
  - Changes to testing approaches or fixture patterns
  - New directory structures or file organizations

- ✅ **Usually Required**:
  - Modified workflows or development processes
  - Updated external dependencies with new patterns
  - Changes to error handling or validation approaches

- ⚠️ **Consider Updating**:
  - Internal implementation changes that affect usage examples
  - Performance optimizations that change recommended patterns
  - Bug fixes that reveal incorrect documentation

- ❌ **Documentation Not Needed**:
  - Pure refactoring with no interface changes
  - Minor variable renaming or code cleanup
  - Internal optimizations with no external impact

### Implementation Status Indicators

Use clear status indicators when documenting features:

```markdown
## Implementation Status
- ✅ **Fully Implemented**: Feature is complete and tested
- 🚧 **Partial Implementation**: Basic functionality exists, advanced features pending
- 📋 **Planned**: Feature is designed but not yet implemented
- ⚠️ **Legacy**: Feature exists but may be deprecated in future versions
```

### Architecture Decision Documentation

When documenting architectural choices, include the rationale:

```markdown
## Why This Pattern
- **Pattern Chosen**: Unit of Work over direct repository access
- **Rationale**: Centralized transaction management across multiple repositories
- **Trade-offs**: Slight complexity increase for transaction safety and consistency
- **Alternatives Considered**: Individual repository transactions, service-level transactions
```

### Cross-Reference Validation

Include dependency information to catch breaking changes:

```markdown
## Dependencies
- **Requires**: `src/cve_tool/repositories/base.py` (BaseRepository class)
- **Used By**: All domain-specific repositories
- **See Also**: `repositories/CLAUDE.md` for usage patterns
```

### Quality Standards

- **Current Implementation Only**: Document what actually exists, not what's planned
- **Working Examples**: All code examples must be tested and functional
- **Clear Scope**: Each CLAUDE.md should have a clear, focused scope
- **Consistent Style**: Follow the established documentation patterns across modules
- **Error-Free**: Documentation should not contain broken links or non-existent references

## Project Memories

- **CRITICAL: Use UV for ALL Python commands**. Always use `uv run` prefix for Python commands (e.g., `uv run pytest`, `uv run python`, etc.). No need to manually activate virtual environments.
- This project uses UV for dependency management with Python 3.12.10. Use `uv sync` to install dependencies and `uv add/remove` to manage them.
- **Python 3.12 Performance Benefits**: The project now uses Python 3.12.10 which provides ~5% overall performance improvement, up to 2x faster comprehensions, and 75% faster asyncio compared to Python 3.11.
- All fixtures should be created in the backend/tests/fixtures directory (when reorganized) and registered in backend/tests/conftest.py as plugins.
- All pytest tests should be written as function-style, not class-style
- Your first action in any chat should be to check which git branch we are on before trying to perform any actions and determine if a new branch should be created
- We don't create monolithic files. Prioritize single responsibility over all else.
- Never do imports inside methods or functions. That's a complete anti-pattern and very strong code smell.
- Never add special handling to implementation code just to get a test to pass. That's a very clear anti-pattern.
- **Don't say a task is complete until you've verified all new tests created for that task are passing, at a minimum.**
- **DATETIME USAGE**: There is an inconsistency in datetime handling in this codebase - some code uses timezone-aware datetimes with UTC, while other code (especially in models and the database) uses naive datetimes. This needs to be standardized:
  - Replace deprecated `datetime.utcnow()` with `datetime.now(UTC)` in new code
  - When comparing datetimes from the database (naive) with timezone-aware datetimes, either:
    - Convert database values to timezone-aware: `datetime.combine(db_date.date(), db_date.time(), UTC)`
    - Or strip timezone from aware dates: `aware_date.replace(tzinfo=None)`
  - A long-term fix should standardize all date handling to use timezone-aware datetimes with UTC
  - Consider adding SQLAlchemy type adapters to automatically convert between naive DB datetimes and timezone-aware application datetimes
- Since this is a dev database, we don't need to fight with complex Alembic migrations. The dev DB can be destroyed and re-initialized as needed during development.

- **USE CONTEXT7 REGULARLY**: When writing code that uses external packages (Pydantic, SQLAlchemy, FastAPI, etc.), use the Context7 service to check the latest documentation and best practices. This ensures we're always using current features and avoiding deprecated patterns. Especially valuable when implementing validators, schemas, or any package-specific functionality.

## Task File Management Protocol

**CRITICAL**: Always check for completed tasks during end of session protocol. This is frequently missed!

When working with task files in `docs/tasks/`:

### During Implementation

1. **Update Original Task File**: Add implementation details, discoveries, and results directly to the original task file
2. **Document Blockers**: If you discover architectural issues or dependencies, document them in the original file
3. **Never Create Copies**: Don't create duplicate files with suffixes like `_COMPLETED` or `_DONE`

### Task Completion Checklist

Before ending any coding session, ask these questions:

1. ✅ **Are all acceptance criteria in the task file met?**
   - If YES → Move to completed directory
   - If NO → Update task file with current status and remaining work

2. ✅ **Did I verify all new tests are passing?**
   - Required before marking any task complete

3. ✅ **Did I document the implementation results in the task file?**
   - Add performance results, design decisions, discovered issues

### Completion Process

```bash
# First: Update the task file with final results and learnings
# Then: Move to completed directory
git mv docs/tasks/task_name.md docs/tasks/completed/
# Include in your final commit
```

### Common Mistakes

- ❌ **Most Common**: Forgetting to move completed tasks to `docs/tasks/completed/`
- ❌ Creating `task_name_COMPLETED.md` files instead of moving
- ❌ Moving incomplete tasks to completed directory
- ❌ Not documenting implementation results before moving

## CHANGELOG.md Update Guidelines

- Never remove anything from CHANGELOG.md
- Always add new entries near the top below these lines:

```markdown
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

## End Coding Session Protocol

When completing a coding session, follow this procedure based on the current branch:

### For Feature Branch Work (Most Common)

1. **Check Task Completion Status** ⚠️ **CRITICAL STEP - FREQUENTLY MISSED**
   - Review the Task File Management Protocol checklist above
   - If all acceptance criteria are met: Move task file to `docs/tasks/completed/`
   - If work remains: Update task file with current status and remaining work
   - Always include task file changes in your final commit

2. **Review and Finalize Implementation**
   - Review any task documentation or requirements that were being worked on
   - Verify that all requirements and acceptance criteria have been met
   - Run tests to ensure new functionality works correctly
   - Document the current state and any remaining work

3. **Stage Changes and Commit to Feature Branch**
   - Stage all modified files using `git add` (including task file moves/updates)
   - Create a commit with a structured message following the format below
   - DO NOT update version numbers or CHANGELOG.md in feature branches

4. **Push Changes to Remote**
   - Push the feature branch to the remote repository using `git push`
   - If this is the first push for a new branch, use `git push -u origin branch-name`
   - For existing branches, use `git push` to update the remote with your commits

### Commit Message Structure for Feature Branches

```markdown
[Type] Component: Brief description

- Change 1
- Change 2
- Change 3

[Brief explanation of why changes were made]
```

Types: `[Add]`, `[Fix]`, `[Update]`, `[Refactor]`, `[Remove]`, etc.

Example workflow for feature branches:

```bash
# Include all modified files
git add backend/app/models/ backend/tests/ [other modified files]
git commit -m "[Add] Question Management: Implement question model and validation

- Added QuestionModel with difficulty levels and relationships
- Created question schema validation with Pydantic
- Added CRUD operations for question management

Implements the foundation for quiz question handling"

# Push to remote repository
git push  # or git push -u origin feature-branch-name for first push
```

### For Dev Branch Merges

When merging a feature branch into `dev` via a Pull Request:

1. Create a PR from your feature branch to `dev`
2. Review the code changes
3. Merge the feature branch into `dev`
4. No version updates or CHANGELOG changes yet

### For Main Branch Releases

Only when preparing a release from `dev` to `main`:

1. **Update Version Information**
   - Use semantic versioning (MAJOR.MINOR.PATCH)
   - Update version information in `pyproject.toml`

2. **Update CHANGELOG.md**
   - Add new version entry (format: `## [x.y.z] - YYYY-MM-DD`)
   - Document changes under appropriate categories (Added, Changed, Fixed, etc.)
   - Include all significant changes from feature merges
   - Reference related ADRs or issues

3. **Create a release PR from `dev` to `main`**
   - Include version bumps and CHANGELOG updates
   - After approval, merge to `main`

4. **Tag the Release**
   - After merging to `main`, create a version tag:

   ```bash
   git checkout main
   git pull origin main
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   git push origin vX.Y.Z
   ```
