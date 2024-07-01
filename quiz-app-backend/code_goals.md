# Code goals for Quiz App project

## 1. Implement logging stratgy:

---

**Objective:**

We want to remove all explicit logging statements from our FastAPI codebase and implement logging in a more centralized and manageable way. Currently, our logging service is imported into each script where logging is required. The logging service script is as follows:

```python
# app/services/logging_service.py

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import os

class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

    def format(self, record):
        # Add the relative path, function name, and line number to the record
        record.relativepath = os.path.relpath(record.pathname)
        record.funcname = record.funcName
        record.lineno = record.lineno
        return super().format(record)

def setup_logging(disable_logging=False, disable_cli_logging=False):
    logger_setup = logging.getLogger("backend")

    if disable_logging:
        logger_setup.disabled = True
        return logger_setup
    
    logger_setup.setLevel(logging.DEBUG)

    # File Handler
    log_file = "/var/log/quiz-app/backend/backend.log"
    if not disable_logging:
        handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    else:
        handler = logging.NullHandler()  # Redirect logs to /dev/null if logging is disabled

    handler.setLevel(logging.DEBUG)
    formatter = UTCFormatter("%(asctime)s - %(name)s - %(levelname)s - %(relativepath)s - %(funcname)s - line %(lineno)d - %(message)s")
    handler.setFormatter(formatter)
    logger_setup.addHandler(handler)

    # CLI Handler
    if not disable_cli_logging:
        cli_handler = logging.StreamHandler()
        cli_handler.setLevel(logging.DEBUG)
        cli_handler.setFormatter(formatter)
        logger_setup.addHandler(cli_handler)

    return logger_setup

# Example usage:
logger = setup_logging(disable_logging=False, disable_cli_logging=True)
```

**New Logging Strategies:**

We will implement the following strategies to centralize and manage logging more effectively:

### 1. Middleware for Request and Response Logging

Create a middleware to log all incoming requests and outgoing responses.

**Implementation:**

```python
# app/middleware/logging_middleware.py

from fastapi import FastAPI, Request
import logging
import time

app = FastAPI()
logger = setup_logging(disable_logging=False, disable_cli_logging=True)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url} - {response.status_code} - {process_time:.3f}ms")
    return response
```

### 2. SQLAlchemy Event Logging

Use SQLAlchemy events to log database queries and their execution times.

**Implementation:**

```python
# app/database/logging_events.py

from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

logger = setup_logging(disable_logging=False, disable_cli_logging=True)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.info(f"Start Query: {statement}")

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.info(f"End Query: {statement}")
```

### 3. Pydantic Model Validation Logging

Override the `__init__` method in Pydantic models to log data validation.

**Implementation:**

```python
# app/models/logging_models.py

from pydantic import BaseModel, ValidationError
import logging

logger = setup_logging(disable_logging=False, disable_cli_logging=True)

class MyModel(BaseModel):
    name: str
    age: int

    def __init__(self, **data):
        try:
            super().__init__(**data)
            logger.info(f"Validated Data: {data}")
        except ValidationError as e:
            logger.error(f"Validation Error: {e}")
            raise e
```

### 4. Custom Logging Decorators

Create decorators to log function entry, exit, and exceptions.

**Implementation:**

```python
# app/decorators/logging_decorator.py

import logging
import functools

logger = setup_logging(disable_logging=False, disable_cli_logging=True)

def log_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Exiting {func.__name__} with result {result}")
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper

# Example usage
@log_function
def my_function(x, y):
    return x + y
```

### 5. Context Managers for Scoped Logging

Use context managers to log operations within a specific scope.

**Implementation:**

```python
# app/context_managers/logging_context.py

import logging

logger = setup_logging(disable_logging=False, disable_cli_logging=True)

class log_context:
    def __init__(self, context_name):
        self.context_name = context_name

    def __enter__(self):
        logger.info(f"Entering context: {self.context_name}")

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(f"Exception in context: {self.context_name} - {exc_value}")
        logger.info(f"Exiting context: {self.context_name}")

# Example usage
with log_context("Database operation"):
    # perform database operations
    pass
```

**Task:**

1. **Remove explicit logging statements** from the codebase.
2. **Implement the above logging strategies** to ensure logging is centralized and managed effectively.

By using these strategies, we aim to maintain a clean codebase while ensuring robust logging throughout the application.

---

## 2. Identify all missing crud functions, endpoints, and schemas, particularly surrounding association functionality

## 3. Fix broken permissions system that doesn't identify route with IDs, for example:

```

2024-06-23 08:35:11,011 - backend - DEBUG - app/middleware/authorization_middleware.py - dispatch - line 22 - AuthorizationMiddleware - Requested URL: /question-sets/1
2024-06-23 08:35:11,011 - backend - DEBUG - app/middleware/authorization_middleware.py - dispatch - line 28 - AuthorizationMiddleware - Protected endpoint, checking authorization
2024-06-23 08:35:11,011 - backend - DEBUG - app/services/user_service.py - get_current_user - line 18 - get_current_user called with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LnVzZXJfM3R4OG0iLCJleHAiOjE3MTkxMzM1MTB9.2aqOqgfVeNZLkOHXCNK__hTQvFqM0im-gyr4cbQwURw
2024-06-23 08:35:11,012 - backend - DEBUG - app/core/jwt.py - decode_access_token - line 25 - Decoding access token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LnVzZXJfM3R4OG0iLCJleHAiOjE3MTkxMzM1MTB9.2aqOqgfVeNZLkOHXCNK__hTQvFqM0im-gyr4cbQwURw
2024-06-23 08:35:11,012 - backend - DEBUG - app/core/jwt.py - decode_access_token - line 27 - Access token decoded: {'sub': 'test.user_3tx8m', 'exp': 1719133510}
2024-06-23 08:35:11,012 - backend - DEBUG - app/services/user_service.py - get_current_user - line 28 - Token expiration: 2024-06-23 09:05:10+00:00
2024-06-23 08:35:11,014 - backend - DEBUG - app/services/user_service.py - get_current_user - line 40 - User found: <app.models.users.UserModel object at 0x7b202ddb30d0>
2024-06-23 08:35:11,014 - backend - DEBUG - app/middleware/authorization_middleware.py - dispatch - line 35 - Current user: <app.models.users.UserModel object at 0x7b202ddb30d0>
2024-06-23 08:35:11,015 - backend - DEBUG - app/middleware/authorization_middleware.py - dispatch - line 40 - AuthorizationMiddleware - CRUD verb: update
2024-06-23 08:35:11,017 - backend - DEBUG - app/middleware/authorization_middleware.py - dispatch - line 51 - AuthorizationMiddleware - No permission found for the current route and CRUD verb
```

## 4. Remove explicit uses of models from conftest.py and move to using all crud functions where possible

## 5. Ensure endpoints only use crud functions and schemas and do not explicityly use models

## 6. Expand test coverage to include all scripts, classes, and functions

## 7. Return to work items in Azure Board
