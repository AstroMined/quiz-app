# filename: app/api/endpoints/users.py
"""
This module provides a simple endpoint for retrieving user information.

It defines a route for retrieving a list of users (currently hardcoded).
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/users/")
def read_users():
    """
    Endpoint to retrieve a list of users.
    
    Returns:
        A list of user objects (currently hardcoded).
    """
    return [{"username": "user1"}, {"username": "user2"}]