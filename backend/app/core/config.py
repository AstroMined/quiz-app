# filename: backend/app/core/config.py

import os
from enum import Enum as PyEnum

import dotenv
import toml
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from backend.app.services.logging_service import logger


class DifficultyLevel(PyEnum):
    BEGINNER = "Beginner"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

class SettingsCore(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    UNPROTECTED_ENDPOINTS: list

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        logger.debug("Looking for .env file at: %s", env_file)

def load_config_from_toml() -> dict:
    # Adjust path to find pyproject.toml in the quiz-app directory
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "pyproject.toml")
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
        # Load SECRET_KEY from .env
        logger.debug("Loading SECRET_KEY from .env file")
        env_settings = dotenv.dotenv_values(".env")
        secret_key = env_settings.get("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY not found in .env file")
        logger.debug("SECRET_KEY loaded from .env")
    except Exception as e:
        logger.error("Error loading SECRET_KEY from .env: %s", str(e))
        raise
    
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
            SECRET_KEY=secret_key,
            ACCESS_TOKEN_EXPIRE_MINUTES=toml_config["access_token_expire_minutes"],
            DATABASE_URL=database_url,
            UNPROTECTED_ENDPOINTS=toml_config["unprotected_endpoints"],
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
