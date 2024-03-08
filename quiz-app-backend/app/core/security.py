# filename: app/core/security.py
"""
This module provides security-related utilities for the Quiz App backend.

It includes functions for password hashing and verification using the bcrypt algorithm.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Verify a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password to be verified.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Generate a hash for the provided password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The generated hash of the password.
    """
    return pwd_context.hash(password)