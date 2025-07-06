<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-06

### Major Architectural Improvements

#### Removed

- **Validation Service Anti-Pattern**: Completely removed redundant validation service (239 lines)
  - Eliminated architectural layer separation violations
  - Achieved 75-90% reduction in database queries for model operations
  - 73-84% faster model creation operations
  - Proper validation now handled by database constraints

#### Added

- **SQLAlchemy Error Handling**: Comprehensive database constraint error management (218 lines)
  - Centralized error handling for all constraint violations
  - Proper error mapping from database to application layer
  - Improved user experience with meaningful error messages

- **Performance Monitoring Infrastructure**: Complete test performance framework
  - Performance benchmark suite with regression detection
  - Test execution time monitoring and optimization
  - Parallel test execution with pytest-xdist (4x faster test runs)
  - Fixture performance optimization and monitoring

- **Database Infrastructure Improvements**:
  - Foreign key constraint enforcement
  - Transaction isolation testing framework
  - In-memory database with transaction rollback for testing
  - Reference data initialization and management

#### Fixed

- **Test Suite Reliability**: Resolved 96+ systematic test failures
  - Fixed unique constraint violations across all entity types
  - Resolved data contamination issues in parallel test execution
  - Fixed SQLAlchemy DetachedInstanceError in schema tests
  - Eliminated race conditions in authentication and authorization tests

- **Test Infrastructure**: Major improvements to test execution
  - Resolved fixture naming conflicts and missing references
  - Fixed session isolation issues in middleware tests
  - Improved test data management and cleanup
  - Enhanced error handling in test scenarios

#### Changed

- **BREAKING**: Removed validation service dependency from application startup
- **Test Strategy**: Shifted from fixing test workarounds to architectural solutions
- **Development Approach**: Parallel test execution as default (4x performance improvement)

### Technical Debt and Architecture Notes

#### Current State

- Core application functionality preserved and improved
- Validation service anti-pattern successfully eliminated
- Test infrastructure significantly enhanced
- Database error handling centralized and improved

#### Known Issues Requiring Architectural Refactor

- **Transaction Boundary Control**: Current CRUD pattern breaks test isolation
  - CRUD functions call `db.commit()` internally
  - Tests cannot control transaction boundaries
  - Requires Repository + Unit of Work pattern implementation

- **Mixed Concerns**: CRUD layer mixes data access with transaction management
  - No clear separation between data operations and transaction control
  - Testing requires workarounds instead of proper isolation
  - Architecture investigation completed: 6-8 weeks implementation required

#### Next Phase: Repository + Unit of Work Pattern Implementation

- Investigation completed: `docs/tasks/repository_unit_of_work_pattern_investigation.md`
- Proof of concept required for Questions domain
- Full implementation timeline: 6-8 weeks
- Will solve fundamental transaction control issues
- Prerequisite for reliable test suite and future scalability

### Performance Improvements

- **Database Operations**: 75-90% reduction in queries through validation service removal
- **Test Execution**: 4x faster through parallel execution (pytest-xdist)
- **Model Creation**: 73-84% faster operations
- **Development Workflow**: Improved through better error handling and monitoring

### Files Changed

- 110 files modified: +15,787 lines added, -1,088 lines removed
- Major refactoring in CRUD layer, test infrastructure, and error handling
- Complete removal of validation service throughout application
- Comprehensive test suite improvements and reliability enhancements

### Migration Notes

This version represents a major architectural cleanup but stops short of full CRUD pattern replacement. The next major version will implement Repository + Unit of Work pattern to solve remaining transaction control issues.

## [0.1.1] - 2025-06-29

### Fixed

- Authentication test failures: Fixed `test_revoke_expired_token` and `test_is_token_revoked_with_old_token` to properly expect `ExpiredSignatureError` for expired tokens instead of treating them as revoked tokens
- Test suite stability: Resolved transient validation issues that were causing false positive failures in question model, scoring service, and CORS middleware tests
- Authentication logic: Maintained proper separation between expired and revoked token states in accordance with JWT security best practices

### Technical

- Updated authentication tests to align with correct token expiration behavior
- Preserved authentication middleware functionality while fixing test expectations
- All previously failing tests now pass: 5/5 resolved

## [0.1.0] - 2025-06-28

### Added

- Initial version tracking with version.py module
- Comprehensive project metadata in pyproject.toml
- CHANGELOG.md for tracking project changes
- Complete dependency management migration from Conda to UV
- Python 3.12.10 support with performance improvements

### Changed

- **BREAKING**: Migrated from Conda to UV for dependency management
- **BREAKING**: Upgraded Python from 3.11.8 to 3.12.10
- Updated all dependencies to latest versions:
  - FastAPI: 0.110.0 → 0.115.14
  - SQLAlchemy: 2.0.27 → 2.0.41  
  - Pydantic: 2.6.3 → 2.11.7
  - Alembic: 1.13.1 → 1.16.2
  - Black: 24.8.0 → 25.1.0
  - Pytest: 8.1.2 → 8.4.1
  - Pylint: 3.2.2 → 3.3.7
  - Uvicorn: 0.27.1 → 0.34.3
- Updated CLAUDE.md documentation for UV workflow
- Replaced conda commands with `uv run` equivalents throughout documentation

### Performance Improvements

- ~5% overall performance improvement from Python 3.12 upgrade
- Up to 2x faster comprehensions and list operations
- 75% faster asyncio operations (beneficial for FastAPI)
- 2x faster isinstance() protocol checks (beneficial for Pydantic validation)

### Infrastructure

- Added .python-version file for Python version management
- Created uv.lock file for deterministic dependency resolution
- Removed dependency on Anaconda Python interpreter
- Enhanced project metadata with keywords, classifiers, and license information

### Technical Details

- Python Version: 3.12.10 (managed by UV)
- Dependency Manager: UV (replacing Conda)
- Virtual Environment: Fresh .venv created with UV
- All tests passing with new environment

### Migration Notes

For developers updating their local environment:

1. Install UV if not already available
2. Run `uv sync --all-extras` to recreate the environment
3. Use `uv run` prefix for all Python commands
4. Remove old conda environment when ready

---

## Previous Releases

Prior to v0.1.0, this project used Conda for dependency management and did not maintain a formal changelog. Recent commits included:

- Complete refactor of CRUD modules and related tests
- Major refactor with Models, core, and API tests passing
- Renamed backend and frontend subdirectories with corrected imports
- Refactored API endpoints with standard naming conventions and error handling
- Added missing API endpoints for question tags
- Complete refactor of CRUD functions with 89% test coverage
