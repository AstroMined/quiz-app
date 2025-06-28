# filename: backend/tests/conftest.py

import os
import sys

import pytest

from backend.app.services.logging_service import logger

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


@pytest.fixture(autouse=True)
def log_test_name(request):
    """Log the start and end of each test for debugging purposes."""
    logger.debug("Running test: %s", request.node.nodeid)
    yield
    logger.debug("Finished test: %s", request.node.nodeid)