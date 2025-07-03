# Implement SQLAlchemy Error Handling

## Task Overview

**Status**: 🔴 **Pending**  
**Priority**: High  
**Complexity**: Medium  
**Estimated Effort**: 2-3 hours  

## Problem Summary

After removing the validation service anti-pattern, the application needs proper error handling for database constraint violations. This task implements clean SQLAlchemy error handling that catches `IntegrityError` exceptions and transforms them into user-friendly HTTP responses, maintaining the same API contract while using proper architectural patterns.

## Implementation Strategy

### SQLAlchemy-Native Error Handling

**Approach**: Let database constraint violations bubble up naturally as `sqlalchemy.exc.IntegrityError`, then handle them at the appropriate API layer.

**Benefits**:
- Proper separation of concerns (database handles data integrity)
- SQLAlchemy error messages are descriptive and accurate
- No custom error mapping layer to maintain
- Consistent handling for all constraint types (FK, unique, check, etc.)
- Future-proof (new constraints automatically get proper handling)

### Error Handling Architecture

#### Layer Responsibilities

1. **Database Layer**: Enforce constraints, generate IntegrityError
2. **API Layer**: Catch IntegrityError, transform to HTTP 400 responses
3. **Client Layer**: Receive consistent HTTP 400 responses with clear messages

#### Error Flow

```
Database Constraint Violation
    ↓
SQLAlchemy IntegrityError
    ↓
API Error Handler
    ↓
HTTP 400 Bad Request
    ↓
Client Error Response
```

## Implementation Components

### 1. Database Error Handler Middleware

**File**: `backend/app/middleware/database_error_middleware.py`

**Purpose**: Catch all `IntegrityError` exceptions and transform them to HTTP responses

**Functionality**:
- Intercept `sqlalchemy.exc.IntegrityError` from any endpoint
- Parse constraint violation details
- Generate appropriate HTTP 400 responses
- Maintain consistent error response format

### 2. Error Message Parsing

**Component**: Constraint violation message parser

**Purpose**: Extract meaningful information from SQLAlchemy error messages

**Functionality**:
- Parse foreign key constraint failures
- Parse unique constraint violations
- Parse check constraint failures
- Extract field names and values from error messages

### 3. API Error Response Format

**Standard Format**:
```json
{
  "error": "Constraint Violation",
  "detail": "Invalid role_id: 999",
  "type": "foreign_key_violation",
  "field": "role_id",
  "value": 999
}
```

### 4. Integration with FastAPI

**Integration Points**:
- Exception handlers for `IntegrityError`
- Middleware for automatic error catching
- Consistent error response across all endpoints

## Technical Implementation

### Database Error Middleware

```python
# backend/app/middleware/database_error_middleware.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import re

class DatabaseErrorMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                await send(message)
            elif message["type"] == "http.response.body":
                await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except IntegrityError as e:
            response = self.handle_integrity_error(e)
            await response(scope, receive, send)

    def handle_integrity_error(self, error: IntegrityError) -> JSONResponse:
        """Transform IntegrityError to user-friendly HTTP response."""
        
        error_detail = self.parse_constraint_error(str(error))
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Constraint Violation",
                "detail": error_detail["message"],
                "type": error_detail["type"],
                "field": error_detail.get("field"),
                "value": error_detail.get("value")
            }
        )

    def parse_constraint_error(self, error_message: str) -> dict:
        """Parse SQLAlchemy constraint error messages."""
        
        # Foreign key constraint pattern
        fk_pattern = r"FOREIGN KEY constraint failed"
        if re.search(fk_pattern, error_message):
            return self.parse_foreign_key_error(error_message)
        
        # Unique constraint pattern
        unique_pattern = r"UNIQUE constraint failed: (\w+)\.(\w+)"
        unique_match = re.search(unique_pattern, error_message)
        if unique_match:
            table, field = unique_match.groups()
            return {
                "type": "unique_violation",
                "field": field,
                "message": f"A record with this {field} already exists"
            }
        
        # Generic constraint violation
        return {
            "type": "constraint_violation",
            "message": "Database constraint violation occurred"
        }

    def parse_foreign_key_error(self, error_message: str) -> dict:
        """Parse foreign key constraint errors."""
        
        # Extract field information from INSERT statement if available
        insert_pattern = r"INSERT INTO (\w+) \([^)]*(\w+_id)[^)]*\) VALUES \([^)]*(\d+)[^)]*\)"
        insert_match = re.search(insert_pattern, error_message)
        
        if insert_match:
            table, field, value = insert_match.groups()
            return {
                "type": "foreign_key_violation",
                "field": field,
                "value": int(value),
                "message": f"Invalid {field}: {value}"
            }
        
        return {
            "type": "foreign_key_violation",
            "message": "Invalid foreign key reference"
        }
```

### FastAPI Exception Handlers

```python
# backend/app/api/error_handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

def add_error_handlers(app: FastAPI):
    """Add database error handlers to FastAPI app."""
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity constraint violations."""
        
        logger.warning(f"Database integrity error: {exc}")
        
        # Parse the error message for user-friendly response
        error_detail = parse_integrity_error(str(exc))
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Constraint Violation",
                "detail": error_detail["message"],
                "type": error_detail["type"]
            }
        )

def parse_integrity_error(error_message: str) -> dict:
    """Parse SQLAlchemy IntegrityError messages into user-friendly format."""
    
    if "FOREIGN KEY constraint failed" in error_message:
        return {
            "type": "foreign_key_violation",
            "message": "Referenced record does not exist"
        }
    elif "UNIQUE constraint failed" in error_message:
        return {
            "type": "unique_violation", 
            "message": "A record with these values already exists"
        }
    else:
        return {
            "type": "constraint_violation",
            "message": "Database constraint violation"
        }
```

### Integration with Main Application

```python
# backend/app/main.py - Integration

from backend.app.api.error_handlers import add_error_handlers

app = FastAPI()

# Add error handlers
add_error_handlers(app)

# ... rest of application setup
```

## Error Message Mapping

### Common Constraint Violations (From Database Constraint Audit)

| Database Error | User-Friendly Message | HTTP Status | Error Type |
|---------------|----------------------|-------------|------------|
| `FOREIGN KEY constraint failed` | `Invalid {field}: {value}` | 400 | `foreign_key_violation` |
| `UNIQUE constraint failed: users.email` | `A user with this email already exists` | 400 | `unique_violation` |
| `UNIQUE constraint failed: users.username` | `A user with this username already exists` | 400 | `unique_violation` |
| `UNIQUE constraint failed: groups.name` | `A group with this name already exists` | 400 | `unique_violation` |
| `CHECK constraint failed` | `Invalid value for {field}` | 400 | `check_violation` |

### Specific Foreign Key Constraints (38 total identified)

**High-Impact FK Constraints** (frequent operations):
- `users.role_id` → `roles.id` (RESTRICT - cannot delete role with users)
- `user_responses.user_id` → `users.id` (CASCADE - cleanup when user deleted)
- `user_responses.question_id` → `questions.id` (CASCADE - cleanup when question deleted)
- `user_responses.answer_choice_id` → `answer_choices.id` (SET NULL - preserve response if answer deleted)
- `leaderboards.user_id` → `users.id` (CASCADE)
- `leaderboards.group_id` → `groups.id` (CASCADE) 
- `leaderboards.time_period_id` → `time_periods.id` (RESTRICT)

**Creator FK Constraints** (SET NULL pattern):
- `questions.creator_id` → `users.id` (SET NULL - preserve content when creator deleted)
- `groups.creator_id` → `users.id` (SET NULL)
- `question_sets.creator_id` → `users.id` (SET NULL)

### Field-Specific Messages

**User-Friendly Field Names** (from constraint audit):
- `role_id` → "role"
- `user_id` → "user"
- `question_id` → "question"
- `answer_choice_id` → "answer choice"
- `group_id` → "group"
- `time_period_id` → "time period"
- `creator_id` → "creator"
- `subject_id` → "subject"
- `topic_id` → "topic"
- `subtopic_id` → "subtopic"
- `concept_id` → "concept"
- `discipline_id` → "discipline"
- `domain_id` → "domain"
- `question_set_id` → "question set"
- `question_tag_id` → "question tag"
- `permission_id` → "permission"

## Testing Strategy

### Unit Tests for Error Handling

**Test Cases**:
1. Foreign key constraint violations
2. Unique constraint violations
3. Check constraint violations
4. Error message parsing accuracy
5. HTTP response format consistency

### Integration Tests

**Test Scenarios**:
1. API endpoints with invalid foreign keys
2. API endpoints with duplicate unique fields
3. Error response format verification
4. Status code verification

### Test Implementation

```python
# backend/tests/integration/test_database_error_handling.py

def test_foreign_key_violation_handling(client, db_session):
    """Test that foreign key violations return proper HTTP 400."""
    
    # Attempt to create user with invalid role_id
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass",
        "role_id": 9999  # Invalid foreign key
    })
    
    assert response.status_code == 400
    assert response.json()["error"] == "Constraint Violation"
    assert "Invalid role_id" in response.json()["detail"]
    assert response.json()["type"] == "foreign_key_violation"

def test_unique_constraint_violation_handling(client, test_user):
    """Test that unique violations return proper HTTP 400."""
    
    # Attempt to create user with duplicate email
    response = client.post("/users/", json={
        "username": "newuser",
        "email": test_user.email,  # Duplicate email
        "password": "testpass",
        "role_id": 1
    })
    
    assert response.status_code == 400
    assert response.json()["error"] == "Constraint Violation"
    assert "email already exists" in response.json()["detail"]
    assert response.json()["type"] == "unique_violation"
```

## Implementation Steps

### Step 1: Create Error Handler Infrastructure
- [ ] Create `backend/app/middleware/database_error_middleware.py`
- [ ] Create `backend/app/api/error_handlers.py`
- [ ] Implement constraint error parsing functions

### Step 2: Integrate with FastAPI Application
- [ ] Add error handlers to main application
- [ ] Test error handler integration
- [ ] Verify error response formats

### Step 3: Create Comprehensive Tests
- [ ] Unit tests for error parsing
- [ ] Integration tests for API error responses
- [ ] Test all constraint violation types

### Step 4: Validate Error Behavior
- [ ] Test foreign key violations
- [ ] Test unique constraint violations
- [ ] Verify error message quality and consistency

## Success Criteria

- [ ] All database constraint violations result in HTTP 400 responses
- [ ] Error messages are user-friendly and informative
- [ ] Error response format is consistent across all endpoints
- [ ] No unhandled `IntegrityError` exceptions reach the client
- [ ] API maintains same error contract as before (status codes)
- [ ] All tests pass with new error handling

## Benefits of This Approach

### Architectural Benefits
- **Proper Layer Separation**: Database handles integrity, API handles user communication
- **Future-Proof**: New constraints automatically get error handling
- **Consistent**: All constraint types handled uniformly
- **Maintainable**: No custom validation logic to maintain

### User Experience Benefits
- **Clear Error Messages**: Users understand what went wrong
- **Consistent Format**: Predictable error response structure
- **Appropriate Status Codes**: HTTP 400 for client errors

### Developer Experience Benefits
- **Predictable Errors**: Constraint violations always result in same error type
- **Easy Debugging**: SQLAlchemy errors provide clear constraint information
- **No Hidden Behavior**: Error handling is visible and explicit

## Risk Mitigation

### Error Message Quality
- Parse common constraint patterns for user-friendly messages
- Provide fallback messages for unparseable errors
- Log raw errors for debugging while showing friendly messages to users

### Performance Impact
- Error handling only activates on constraint violations (exceptional cases)
- No performance impact on successful operations
- Simpler than previous validation service (no N+1 queries)

## Next Steps

After successful implementation:
1. Update test suite to expect new error types (Task 2.3)
2. Measure performance improvements (Task 3.1)
3. Update architecture documentation (Task 3.2)

---

**Last Updated**: 2025-07-03  
**Assigned To**: Development Team  
**Dependencies**: Task 2.1 (Validation Service Removal)  
**Blocking**: Task 2.3 (Test Suite Updates)