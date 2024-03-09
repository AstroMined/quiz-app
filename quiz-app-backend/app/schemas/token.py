# filename: app/schemas/token.py
"""
This module defines the Pydantic schema for the Token model.
"""

from pydantic import BaseModel

class Token(BaseModel):
    """
    The schema representing an access token.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of the token.
    """
    access_token: str
    token_type: str
