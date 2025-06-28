# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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