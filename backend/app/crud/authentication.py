# filename: backend/app/crud/authentication.py

"""
This module handles authentication-related database operations.

It provides functions for managing revoked tokens, checking token validity,
and revoking tokens for users. The module interacts with the database
to store and retrieve information about revoked tokens.

Key dependencies:
- sqlalchemy.orm: For database session management
- jose: For JWT token decoding
- backend.app.core.jwt: For access token decoding
- backend.app.crud.crud_user: For user-related database operations
- backend.app.models.authentication: For the RevokedTokenModel
- backend.app.services.logging_service: For logging

Main functions:
- create_revoked_token_in_db: Creates a new revoked token entry
- read_revoked_token_from_db: Retrieves a revoked token from the database
- is_token_revoked: Checks if a token is revoked
- revoke_all_tokens_for_user: Revokes all active tokens for a user
- revoke_token: Revokes a specific token

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.authentication import is_token_revoked

    def check_token_validity(db: Session, token: str):
        if is_token_revoked(db, token):
            return "Token is revoked or invalid"
        return "Token is valid"
"""

from datetime import datetime, timezone

from jose import ExpiredSignatureError
from sqlalchemy.orm import Session

from backend.app.core.jwt import decode_access_token
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.models.authentication import RevokedTokenModel
from backend.app.services.logging_service import logger


def create_revoked_token_in_db(
    db: Session, jti: str, token: str, user_id: int, expires_at: int
) -> RevokedTokenModel:
    """
    Create a new revoked token entry in the database.

    Args:
        db (Session): The database session.
        jti (str): The JWT ID of the token.
        token (str): The full token string.
        user_id (int): The ID of the user associated with the token.
        expires_at (int): The expiration timestamp of the token.

    Returns:
        RevokedTokenModel: The created revoked token database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        revoked_token = create_revoked_token_in_db(db, "token_jti",
            "full_token_string", 1, 1630000000
        )
    """
    # Convert Unix timestamp to datetime object
    expires_at_datetime = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    db_revoked_token = RevokedTokenModel(
        jti=jti,
        token=token,
        user_id=user_id,
        expires_at=expires_at_datetime,
        revoked_at=datetime.now(timezone.utc),
    )
    db.add(db_revoked_token)
    db.commit()
    db.refresh(db_revoked_token)
    return db_revoked_token


def read_revoked_token_from_db(db: Session, token: str) -> RevokedTokenModel:
    """
    Retrieve a revoked token from the database.

    Args:
        db (Session): The database session.
        token (str): The full token string to search for.

    Returns:
        RevokedTokenModel: The revoked token database object if found, None otherwise.

    Usage example:
        revoked_token = read_revoked_token_from_db(db, "full_token_string")
        if revoked_token:
            print("Token is revoked")
    """
    return db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()


def is_token_revoked(db: Session, token: str) -> bool:
    """
    Check if a token is revoked (but NOT expired).

    This function decodes the token, checks its validity, and verifies if it's in the 
    revoked tokens table or if it was issued before the user's token blacklist date.
    
    Note: This function does NOT handle token expiration - expired tokens should be
    handled separately to provide appropriate error messages.

    Args:
        db (Session): The database session.
        token (str): The full token string to check.

    Returns:
        bool: True if the token is revoked, False otherwise.

    Raises:
        ExpiredSignatureError: If the token has expired (not caught - let caller handle).

    Usage example:
        try:
            if is_token_revoked(db, "full_token_string"):
                print("Token is revoked")
            else:
                print("Token is valid and not revoked")
        except ExpiredSignatureError:
            print("Token has expired")
    """
    # Let ExpiredSignatureError bubble up - don't catch it here
    decoded_token = decode_access_token(token, db)

    jti = decoded_token.get("jti")
    username = decoded_token.get("sub")
    token_iat = decoded_token.get("iat")

    if not jti or not username or not token_iat:
        logger.warning(
            "Invalid token format: jti=%s, username=%s, iat=%s",
            jti,
            username,
            token_iat,
        )
        return True  # Consider invalid tokens as revoked

    user = read_user_by_username_from_db(db, username)
    if not user:
        logger.warning("User not found for token: username=%s", username)
        return True  # Consider tokens for non-existent users as revoked

    # Check if the token is in the revoked tokens table
    revoked_token = (
        db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
    )
    if revoked_token:
        logger.info("Token found in revoked tokens table: jti=%s", jti)
        return True

    # Check if the token was issued before the user's token_blacklist_date
    if user.token_blacklist_date:
        token_iat_datetime = datetime.fromtimestamp(token_iat, tz=timezone.utc)
        if token_iat_datetime < user.token_blacklist_date:
            logger.info(
                "Token issued before blacklist date: iat=%s, blacklist_date=%s",
                token_iat_datetime,
                user.token_blacklist_date,
            )
            return True

    logger.info("Token is not revoked: jti=%s", jti)
    return False


def revoke_all_tokens_for_user(db: Session, user_id: int, active_tokens: list):
    """
    Revoke all tokens for a given user.

    This function creates new revoked token entries for all active tokens of the user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose tokens should be revoked.
        active_tokens (list): List of active tokens for the user.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there's an issue with the database operations.

    Usage example:
        active_tokens = ["token1", "token2", "token3"]
        revoke_all_tokens_for_user(db, 1, active_tokens)
    """
    current_time = datetime.now(timezone.utc)

    for token in active_tokens:
        try:
            decoded_token = decode_access_token(token, db)
        except ExpiredSignatureError:
            continue  # Skip expired tokens

        jti = decoded_token.get("jti")
        expires_at = decoded_token.get("exp")

        if not jti or not expires_at:
            continue  # Skip invalid tokens

        # Check if the token is already revoked
        existing_revoked_token = (
            db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
        )
        if existing_revoked_token:
            existing_revoked_token.revoked_at = current_time
        else:
            create_revoked_token_in_db(db, jti, token, user_id, expires_at)

    db.commit()


def revoke_token(db: Session, token: str):
    """
    Revoke a specific token.

    This function creates a new revoked token entry for the given token if it's not already revoked.
    It also handles expired tokens by considering them as already revoked.

    Args:
        db (Session): The database session.
        token (str): The token to be revoked.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there's an issue with the database operations.

    Usage example:
        revoke_token(db, "full_token_string")
    """
    try:
        decoded_token = decode_access_token(token, db)
    except ExpiredSignatureError:
        logger.info("Attempted to revoke an expired token")
        return  # Consider expired tokens as already revoked

    jti = decoded_token.get("jti")
    username = decoded_token.get("sub")
    expires_at = decoded_token.get("exp")

    if not jti or not username or not expires_at:
        logger.warning("Invalid token format")
        return

    user = read_user_by_username_from_db(db, username)
    if not user:
        logger.warning("User not found for token: username=%s", username)
        return

    # Check if the token is already revoked
    existing_revoked_token = (
        db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
    )
    if existing_revoked_token:
        logger.info("Token already revoked: jti=%s", jti)
        return

    create_revoked_token_in_db(db, jti, token, user.id, expires_at)
