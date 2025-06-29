# filename: backend/tests/conftest.py

import os
import sys
import time

import pytest

from backend.app.services.logging_service import logger
from backend.tests.helpers.performance import PerformanceTracker, categorize_test_name

# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Set the environment to test for pytest
os.environ["ENVIRONMENT"] = "test"

# Register all fixture modules as pytest plugins
pytest_plugins = [
    "backend.tests.fixtures.database.session_fixtures",
    "backend.tests.fixtures.models.user_fixtures",
    "backend.tests.fixtures.models.content_fixtures", 
    "backend.tests.fixtures.models.quiz_fixtures",
    "backend.tests.fixtures.schemas.user_schema_fixtures",
    "backend.tests.fixtures.schemas.content_schema_fixtures",
    "backend.tests.fixtures.schemas.quiz_schema_fixtures",
    "backend.tests.fixtures.api.auth_fixtures",
    "backend.tests.fixtures.api.test_data_fixtures",
    "backend.tests.fixtures.integration.complex_data_fixtures",
]


@pytest.fixture(scope="session")
def performance_tracker():
    """Track test performance metrics across the session."""
    return PerformanceTracker()


@pytest.fixture(autouse=True)
def track_test_performance(request, performance_tracker):
    """Automatically track performance for all tests."""
    start_time = time.time()
    logger.debug("Running test: %s", request.node.nodeid)
    yield
    end_time = time.time()
    
    test_duration = end_time - start_time
    test_category = categorize_test_name(str(request.fspath))
    
    performance_tracker.record_test(
        test_name=request.node.nodeid,
        duration=test_duration,
        category=test_category
    )
    
    logger.debug("Finished test: %s (%.3fs, %s)", request.node.nodeid, test_duration, test_category)