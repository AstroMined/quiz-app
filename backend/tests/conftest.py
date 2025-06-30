# filename: backend/tests/conftest.py

import os
import sys
import time

import pytest

from backend.app.services.logging_service import logger
from backend.tests.helpers.performance import PerformanceTracker, categorize_test_name
from backend.tests.helpers.fixture_performance import get_fixture_performance_tracker

# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Set the environment to test for pytest
os.environ["ENVIRONMENT"] = "test"

# Register all fixture modules as pytest plugins
pytest_plugins = [
    "backend.tests.fixtures.database.session_fixtures",
    "backend.tests.fixtures.database.reference_data_fixtures",
    "backend.tests.fixtures.models.user_fixtures",
    "backend.tests.fixtures.models.content_fixtures", 
    "backend.tests.fixtures.models.quiz_fixtures",
    "backend.tests.fixtures.schemas.user_schema_fixtures",
    "backend.tests.fixtures.schemas.content_schema_fixtures",
    "backend.tests.fixtures.schemas.quiz_schema_fixtures",
    "backend.tests.fixtures.api.auth_fixtures",
    "backend.tests.fixtures.api.test_data_fixtures",
    "backend.tests.fixtures.integration.complex_data_fixtures",
    "backend.tests.fixtures.integration.minimal_fixtures",
]


@pytest.fixture(scope="session")
def performance_tracker():
    """Track test performance metrics across the session."""
    return PerformanceTracker()


@pytest.fixture(scope="session")
def fixture_performance_tracker():
    """Track fixture performance metrics across the session."""
    return get_fixture_performance_tracker()


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


def pytest_sessionfinish(session, exitstatus):
    """Report fixture performance at the end of the test session."""
    fixture_tracker = get_fixture_performance_tracker()
    summary = fixture_tracker.get_performance_summary()
    
    if summary:
        logger.info("=== Fixture Performance Summary ===")
        logger.info("Total fixture setups: %d", summary["total_fixture_setups"])
        logger.info("Total setup time: %.3fs", summary["total_setup_time"])
        logger.info("Average setup time: %.3fs", summary["average_setup_time"])
        logger.info("Function-scoped: %d setups (%.3fs)", 
                   summary["function_scoped_setups"], summary["function_scope_time"])
        logger.info("Session-scoped: %d setups (%.3fs)", 
                   summary["session_scoped_setups"], summary["session_scope_time"])
        logger.info("Module-scoped: %d setups (%.3fs)", 
                   summary["module_scoped_setups"], summary["module_scope_time"])
        
        # Report slowest fixtures
        slowest = fixture_tracker.get_slowest_fixtures(5)
        if slowest:
            logger.info("=== Slowest Fixtures ===")
            for fixture_stats in slowest:
                logger.info("%s (%s): avg %.3fs, max %.3fs (%d setups)",
                           fixture_stats["fixture_name"],
                           fixture_stats["scope"],
                           fixture_stats["average_setup_time"],
                           fixture_stats["max_setup_time"],
                           fixture_stats["setup_count"])