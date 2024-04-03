# filename: app/core/__init__.py
"""
This module serves as the main entry point for the core package.

It can be used to perform any necessary initialization or configuration for the core package.
"""
from .config import Settings, settings
from .jwt import create_access_token, verify_token, decode_access_token
from .security import verify_password, get_password_hash
