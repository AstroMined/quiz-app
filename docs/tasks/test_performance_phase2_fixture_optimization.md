# Test Performance Phase 2: Fixture Optimization

## Overview
Optimize complex fixture creation and data setup patterns to reduce test setup overhead and improve reusability.

## Current Problem Analysis

### Complex Fixture Overhead (HIGH)
- **Issue**: `setup_filter_questions_data` creates 50+ database records per test
- **Location**: `backend/tests/fixtures/integration/complex_data_fixtures.py:27-240`
- **Impact**: Heavy object creation for each test that uses filtering functionality
- **Evidence**: 240-line fixture creating domains, disciplines, subjects, topics, subtopics, concepts, question sets, tags

### Fixture Scope Inefficiency (MEDIUM)
- **Issue**: All fixtures are function-scoped, recreating static data unnecessarily
- **Location**: Various fixture files with `scope="function"`
- **Impact**: Repeated creation of reference data that doesn't change between tests

### Fixture Dependency Chains (MEDIUM)
- **Issue**: Complex dependency chains create comprehensive test data every time
- **Location**: API test files requiring multiple model fixtures
- **Impact**: Each test loads full content hierarchy even if only testing basic functionality

## Implementation Tasks

### Task 1: Implement Fixture Scoping Strategy
**Objective**: Use appropriate fixture scopes to minimize data recreation

**Current Pattern**:
```python
@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session, test_model_user_with_group):
    # Creates 50+ objects every test
```

**Target Pattern**:
```python
@pytest.fixture(scope="session")
def base_content_hierarchy():
    # Static reference data - created once per session

@pytest.fixture(scope="module") 
def module_specific_data(base_content_hierarchy):
    # Module-specific data - created once per test file

@pytest.fixture(scope="function")
def test_specific_data(module_specific_data):
    # Only test-specific changes
```

### Task 2: Create Minimal Fixture Variants
**Objective**: Provide lightweight fixtures for simple test cases

**Implementation**:
- `minimal_content_data`: Single subject/topic/concept for basic tests
- `moderate_content_data`: Small hierarchy for relationship tests
- `comprehensive_content_data`: Full hierarchy for complex filtering tests

### Task 3: Implement Fixture Performance Profiling
**Objective**: Identify and measure fixture creation overhead

**Tasks**:
- Add timing decorators to major fixtures
- Create fixture performance report
- Identify slowest fixture creation patterns

### Task 4: Optimize Complex Data Fixtures
**Objective**: Reduce object creation in complex scenarios

**Current Issue**: `setup_filter_questions_data` creates:
- 2 domains
- 2 disciplines  
- 2 subjects
- 2 topics
- 4 subtopics
- 6 concepts
- 3 question sets
- 3 question tags
- 15 questions
- 45 answer choices (3 per question)

**Optimization Strategy**:
- Use factory functions instead of full fixtures for variations
- Implement lazy loading for optional relationships
- Create fixture builders that only create needed objects

## Expected Performance Impact

### Before Optimization
- **Complex Fixture Setup**: 1-2 seconds per test
- **Object Creation**: 50+ database objects per test
- **Fixture Reuse**: Minimal (everything function-scoped)

### After Optimization
- **Complex Fixture Setup**: 0.1-0.3 seconds per test
- **Object Creation**: 5-10 database objects per test (only test-specific)
- **Fixture Reuse**: High (session/module scoped reference data)

**Estimated Improvement**: 30-40% reduction in test setup time

## Implementation Steps

1. **Analyze Current Fixture Usage**
   - Map which tests use which fixtures
   - Identify common vs. unique data requirements
   - Document fixture dependency chains

2. **Design Fixture Hierarchy**
   - Create base fixtures for reference data
   - Design incremental fixture layers
   - Plan scope strategies

3. **Implement Fixture Scoping**
   - Convert static reference data to session scope
   - Create module-scoped fixtures for test file groups
   - Maintain function scope only for test-specific data

4. **Create Minimal Fixture Variants**
   - Implement lightweight alternatives
   - Update tests to use appropriate fixtures
   - Remove over-provisioned fixture usage

5. **Add Performance Monitoring**
   - Implement fixture timing measurement
   - Create performance regression detection
   - Document fixture performance characteristics

## Fixture Categories

### Session-Scoped (Created Once)
- Time periods (already exists)
- Base user roles and permissions
- Core content hierarchy (domains, disciplines)
- System configuration data

### Module-Scoped (Created Per Test File)
- Subject-specific content hierarchies
- Module-specific users and groups
- Test file specific question sets

### Function-Scoped (Created Per Test)
- Test-specific questions and answers
- User responses and scoring data
- Temporary test modifications

## Acceptance Criteria

- [ ] Fixture performance profiling implemented
- [ ] Static reference data moved to session scope
- [ ] Minimal fixture variants created and documented
- [ ] Test setup time reduced by at least 30%
- [ ] All existing tests pass with optimized fixtures
- [ ] Fixture usage documentation updated
- [ ] Performance regression tests implemented

## Risks and Mitigation

**Risk**: Session-scoped fixtures causing test interdependence
**Mitigation**: Careful separation of static vs. mutable data, thorough test isolation verification

**Risk**: Complex fixture hierarchy becoming hard to maintain
**Mitigation**: Clear documentation, logical naming conventions, fixture builder patterns

## Dependencies

**Requires**: Phase 1 completion (fast database operations)
**Enables**: Phase 3 parallel execution (reduced fixture creation overhead)