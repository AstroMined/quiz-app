# filename: backend/app/core/config.py

import os
from enum import Enum as PyEnum
from typing import List

import dotenv
import toml
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings

from backend.app.services.logging_service import logger


class DifficultyLevel(str, PyEnum):
    BEGINNER = "Beginner"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"


class TimePeriod(int, PyEnum):
    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30
    YEARLY = 365

    @classmethod
    def get_name(cls, value):
        return cls(value).name.lower()


class SettingsCore(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    UNPROTECTED_ENDPOINTS: List[str]
    CORS_ORIGINS: List[str]
    ENVIRONMENT: str
    SENTRY_DSN: str = ""  # Optional, empty string as default

    class Config:
        # Define the path to the .env file relative to the location of config.py
        env_file = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            ".env",
        )
        logger.debug("Looking for .env file at: %s", env_file)


def load_config_from_toml() -> dict:
    # Adjust path to find pyproject.toml in the quiz-app directory
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "pyproject.toml",
    )
    logger.debug("Loading configuration from %s", config_path)
    try:
        config = toml.load(config_path)["tool"]["app"]
        logger.debug("Configuration loaded from toml: %s", config)
        return config
    except FileNotFoundError:
        logger.error("pyproject.toml file not found at %s", config_path)
        raise
    except KeyError:
        logger.error("Required 'tool.app' section not found in pyproject.toml")
        raise


def load_settings() -> SettingsCore:
    logger.debug("Entering load_settings()")

    try:
        # Load SECRET_KEY from .env using the path defined in Config
        env_file = SettingsCore.Config.env_file
        logger.debug(f"Loading SECRET_KEY from .env file at {env_file}")
        env_settings = dotenv.dotenv_values(env_file)
        secret_key = env_settings.get("SECRET_KEY")
        if not secret_key:
            raise ValueError(f"SECRET_KEY not found in .env file at {env_file}")
        logger.debug("SECRET_KEY loaded from .env")
    except Exception as e:
        raise ValueError(f"Error loading .env file at {env_file}: {e}")

    try:
        # Load settings from pyproject.toml
        logger.debug("Loading settings from pyproject.toml")
        toml_config = load_config_from_toml()

        # Determine the environment
        environment = os.getenv("ENVIRONMENT", "dev")
        logger.debug("Current environment: %s", environment)

        # Get DATABASE_URL based on environment
        if environment == "dev":
            database_url = toml_config["database_url_dev"]
        elif environment == "test":
            database_url = toml_config["database_url_test"]
        else:
            raise ValueError(f"Invalid environment specified: {environment}")

        logger.debug("Database URL for environment (%s): %s", environment, database_url)

        # Create the settings instance with values from pyproject.toml and .env
        settings = SettingsCore(
            PROJECT_NAME=toml_config["project_name"],
            SECRET_KEY=secret_key,
            ACCESS_TOKEN_EXPIRE_MINUTES=toml_config["access_token_expire_minutes"],
            DATABASE_URL=database_url,
            UNPROTECTED_ENDPOINTS=toml_config["unprotected_endpoints"],
            CORS_ORIGINS=toml_config["cors_origins"],
            ENVIRONMENT=environment,
            SENTRY_DSN=toml_config.get("sentry_dsn", ""),  # Optional
        )

        logger.debug("Settings created: %s", settings.model_dump())
    except KeyError as e:
        logger.error("Missing required setting in pyproject.toml: %s", str(e))
        raise
    except ValidationError as e:
        logger.error("Error creating settings instance: %s", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error loading settings: %s", str(e))
        raise

    logger.debug("Exiting load_settings()")
    return settings


# Load settings based on the environment variable
settings_core = load_settings()


# Add a Pydantic model for JSON serialization
class DifficultyLevelModel(BaseModel):
    difficulty: DifficultyLevel


class TimePeriodModel(BaseModel):
    time_period: TimePeriod
