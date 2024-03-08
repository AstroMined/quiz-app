# filename: app/core/auth.py
"""
This module provides authentication-related functionality for the Quiz App backend.

It defines the OAuth2 authentication scheme and can be extended to include additional authentication mechanisms or utilities.
"""

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")