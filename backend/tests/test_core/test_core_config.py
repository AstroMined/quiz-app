# filename: backend/tests/test_core/test_core_config.py

import os
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from backend.app.core.config import settings_core, load_settings, TimePeriod, load_config_from_toml, SettingsCore

class CustomValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors

def test_settings_core():
    assert isinstance(settings_core.PROJECT_NAME, str)
    assert isinstance(settings_core.SECRET_KEY, str)
    assert isinstance(settings_core.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert isinstance(settings_core.DATABASE_URL, str)
    assert isinstance(settings_core.UNPROTECTED_ENDPOINTS, list)
    assert all(isinstance(endpoint, str) for endpoint in settings_core.UNPROTECTED_ENDPOINTS)

def test_database_url():
    assert settings_core.DATABASE_URL.startswith("sqlite:///")

def test_cors_origins():
    assert isinstance(settings_core.CORS_ORIGINS, list)
    assert all(isinstance(origin, str) for origin in settings_core.CORS_ORIGINS)

def test_environment():
    assert settings_core.ENVIRONMENT in ["dev", "test", "prod"]

def test_sentry_dsn():
    assert isinstance(settings_core.SENTRY_DSN, str)
    # SENTRY_DSN can be an empty string if not set
    if settings_core.SENTRY_DSN:
        assert settings_core.SENTRY_DSN.startswith("https://")

def test_load_settings():
    # This test ensures that the load_settings function works without raising exceptions
    try:
        load_settings()
    except Exception as e:
        pytest.fail(f"load_settings() raised {e} unexpectedly!")

def test_time_period_get_name():
    assert TimePeriod.get_name(TimePeriod.DAILY) == "daily"
    assert TimePeriod.get_name(TimePeriod.WEEKLY) == "weekly"
    assert TimePeriod.get_name(TimePeriod.MONTHLY) == "monthly"
    assert TimePeriod.get_name(TimePeriod.YEARLY) == "yearly"

@patch('backend.app.core.config.toml.load')
def test_load_config_from_toml_file_not_found(mock_toml_load):
    mock_toml_load.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        load_config_from_toml()

@patch('backend.app.core.config.toml.load')
def test_load_config_from_toml_missing_section(mock_toml_load):
    mock_toml_load.return_value = {}
    with pytest.raises(KeyError):
        load_config_from_toml()

@patch('backend.app.core.config.dotenv.dotenv_values')
def test_load_settings_missing_secret_key(mock_dotenv_values):
    mock_dotenv_values.return_value = {}
    with pytest.raises(ValueError, match="SECRET_KEY not found in .env file"):
        load_settings()

@patch('backend.app.core.config.os.getenv')
def test_load_settings_invalid_environment(mock_getenv):
    mock_getenv.return_value = "invalid_env"
    with pytest.raises(ValueError, match="Invalid environment specified"):
        load_settings()

@patch('backend.app.core.config.load_config_from_toml')
def test_load_settings_missing_required_setting(mock_load_config):
    mock_load_config.return_value = {}
    with pytest.raises(KeyError):
        load_settings()

@patch('backend.app.core.config.dotenv.dotenv_values')
@patch('backend.app.core.config.load_config_from_toml')
@patch('backend.app.core.config.SettingsCore')
def test_load_settings_validation_error(mock_settings_core, mock_load_config, mock_dotenv_values):
    mock_dotenv_values.return_value = {"SECRET_KEY": "test_secret"}
    mock_load_config.return_value = {
        "project_name": "Test Project",
        "access_token_expire_minutes": 30,
        "database_url_dev": "sqlite:///./test.db",
        "database_url_test": "sqlite:///./test.db",
        "unprotected_endpoints": [],
        "cors_origins": []
    }
    mock_settings_core.side_effect = CustomValidationError([{"loc": ("field",), "msg": "error message", "type": "value_error"}])
    with pytest.raises(CustomValidationError):
        load_settings()

@patch('backend.app.core.config.dotenv.dotenv_values')
@patch('backend.app.core.config.load_config_from_toml')
def test_load_settings_unexpected_error(mock_load_config, mock_dotenv_values):
    mock_dotenv_values.return_value = {"SECRET_KEY": "test_secret"}
    mock_load_config.return_value = {
        "project_name": "Test Project",
        "access_token_expire_minutes": 30,
        "database_url_dev": "sqlite:///./test.db",
        "database_url_test": "sqlite:///./test.db",
        "unprotected_endpoints": [],
        "cors_origins": []
    }
    with patch('backend.app.core.config.SettingsCore', side_effect=Exception("Unexpected error")):
        with pytest.raises(Exception, match="Unexpected error"):
            load_settings()

# Add more specific tests as needed based on your application's requirements