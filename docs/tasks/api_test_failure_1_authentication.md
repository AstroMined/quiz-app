# API Test Failure Analysis 1: Authentication Token Issues

## Priority: High
**Branch:** `fix/api-test-failures`
**Estimated Time:** 2-3 hours

## Problem Summary

The authentication test suite has a critical failure in token expiration handling:

```
FAILED backend/tests/integration/api/test_authentication.py::test_protected_endpoint_with_expired_token 
- AssertionError: assert 'Token has expired' in 'Token has been revoked'
```

## Failing Test Analysis

### Test: `test_protected_endpoint_with_expired_token`
**Location:** `backend/tests/integration/api/test_authentication.py:61-75`

**Expected Behavior:**
- Create an expired token using `monkeypatch.setattr(settings_core, "ACCESS_TOKEN_EXPIRE_MINUTES", 0)`
- Wait for token to expire
- Access protected endpoint `/users/me` 
- Expect error message: "Token has expired"

**Actual Behavior:**
- Receiving error message: "Token has been revoked"
- Test expects 401 status (which is correct)
- Only the error message text is wrong

## Root Cause Investigation Required

### 1. JWT Token Validation Logic
**Files to examine:**
- `backend/app/core/jwt.py` - Token creation and validation
- `backend/app/core/security.py` - Authentication middleware
- `backend/app/middleware/auth_middleware.py` - Token processing

**Key Questions:**
- How does the system differentiate between expired and revoked tokens?
- Is the expiration check happening before the revocation check?
- Are there multiple code paths that could return "Token has been revoked"?

### 2. Token Blacklist Implementation
**Files to examine:**
- User model token blacklist functionality
- Authentication service token validation flow

**Key Questions:**
- Is there a race condition where tokens are being marked as revoked when they should be marked as expired?
- Does the token blacklist check happen before expiration validation?

### 3. Error Message Consistency
**Investigation needed:**
- Map all authentication error paths
- Ensure consistent error messaging across the authentication flow
- Verify error message constants are properly used

## Implementation Plan

### Phase 1: Reproduce and Isolate (30 minutes)
1. Run the failing test in isolation
2. Add debug logging to understand the exact code path
3. Examine the JWT decode process step by step

### Phase 2: Root Cause Analysis (60 minutes)
1. Trace through `backend/app/core/jwt.py`:
   - `decode_access_token` function
   - Error handling for expired vs revoked tokens
2. Examine authentication middleware:
   - Token validation order
   - Error message generation
3. Check user model and token blacklist logic

### Phase 3: Fix Implementation (45 minutes)
1. Identify the exact location where error message is generated
2. Ensure proper order of checks:
   - Token format validation
   - Token expiration check → "Token has expired"
   - Token revocation check → "Token has been revoked"
3. Update error handling to return correct messages

### Phase 4: Testing and Validation (30 minutes)
1. Run the specific failing test to verify fix
2. Run all authentication tests to ensure no regressions
3. Test edge cases:
   - Token that is both expired and revoked
   - Token with invalid format
   - Token with valid format but expired
   - Token that was manually revoked

## Expected Files to Modify

- `backend/app/core/jwt.py` - Token validation logic
- `backend/app/middleware/auth_middleware.py` - Authentication flow
- Possibly `backend/app/core/security.py` - Security utilities

## Success Criteria

- [ ] `test_protected_endpoint_with_expired_token` passes
- [ ] All other authentication tests continue to pass
- [ ] Error messages are consistent and accurate:
  - Expired tokens return "Token has expired"
  - Revoked tokens return "Token has been revoked"
  - Invalid tokens return "Could not validate credentials"
- [ ] No performance regression in authentication flow

## Testing Commands

```bash
# Run specific failing test
uv run pytest backend/tests/integration/api/test_authentication.py::test_protected_endpoint_with_expired_token -v

# Run all authentication tests
uv run pytest backend/tests/integration/api/test_authentication.py -v

# Run broader auth-related tests if needed
uv run pytest backend/tests/ -k "auth" -v
```

## Notes

- This appears to be a logic/ordering issue rather than a fundamental design problem
- The functionality works (401 status is correct), just the error message is wrong
- May be related to token blacklist implementation that was added in recent changes
- Consider if this reveals other inconsistencies in authentication error handling

## Dependencies

- No external dependencies
- Should not require database schema changes
- No impact on API contract (status codes remain the same)