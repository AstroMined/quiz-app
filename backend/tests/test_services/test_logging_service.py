# filename: backend/tests/test_services/test_logging_service.py

import pytest
import logging
from datetime import datetime, timezone
from backend.app.services.logging_service import sqlalchemy_obj_to_dict, UTCFormatter, setup_logging

class MockSQLAlchemyObj:
    def __init__(self):
        self.id = 1
        self.name = "Test"

    class MockInspector:
        class MockMapper:
            class MockColumnAttr:
                def __init__(self, key):
                    self.key = key
            column_attrs = [MockColumnAttr("id"), MockColumnAttr("name")]
        mapper = MockMapper()

    def __class__(self):
        return type('MockClass', (), {'__mapper__': self.MockInspector.MockMapper()})

def test_sqlalchemy_obj_to_dict():
    obj = MockSQLAlchemyObj()
    result = sqlalchemy_obj_to_dict(obj)
    assert result == {"id": 1, "name": "Test"}

def test_utc_formatter():
    formatter = UTCFormatter()
    record = logging.LogRecord("test", logging.INFO, "test.py", 10, "Test message", (), None)
    record.created = datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp()

    formatted_time = formatter.formatTime(record)
    assert formatted_time.startswith("2023-01-01 00:00:00")

    formatted_record = formatter.format(record)
    assert "test.py" in formatted_record
    assert "line 10" in formatted_record

def test_setup_logging():
    # Test with default settings
    logger = setup_logging()
    assert logger.name == "backend"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1  # Only file handler, CLI logging is disabled by default

    # Test with disabled logging
    disabled_logger = setup_logging(disable_logging=True)
    assert disabled_logger.disabled

    # Test with CLI logging enabled
    cli_logger = setup_logging(disable_cli_logging=False)
    assert len(cli_logger.handlers) == 2  # Both file and CLI handlers

    # Clean up
    logging.getLogger("backend").handlers.clear()

# Note: These tests don't actually write to log files or output to console.
# For more comprehensive testing, you might want to use mock objects or
# temporary directories to capture actual log output.