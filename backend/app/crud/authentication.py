# filename: backend/app/crud/authentication.py

from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.authentication import RevokedTokenModel
from backend.app.core.jwt import decode_access_token
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.services.logging_service import logger

def create_revoked_token_in_db(db: Session, jti: str, token: str, user_id: int, expires_at: int) -> RevokedTokenModel:
    # Convert Unix timestamp to datetime object
    expires_at_datetime = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    db_revoked_token = RevokedTokenModel(jti=jti, token=token, user_id=user_id, expires_at=expires_at_datetime, revoked_at=datetime.now(timezone.utc))
    db.add(db_revoked_token)
    db.commit()
    db.refresh(db_revoked_token)
    return db_revoked_token

def read_revoked_token_from_db(db: Session, token: str) -> RevokedTokenModel:
    return db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()

def is_token_revoked(db: Session, token: str) -> bool:
    decoded_token = decode_access_token(token)
    jti = decoded_token.get("jti")
    username = decoded_token.get("sub")
    token_iat = decoded_token.get("iat")

    if not jti or not username or not token_iat:
        logger.warning(f"Invalid token format: jti={jti}, username={username}, iat={token_iat}")
        return True  # Consider invalid tokens as revoked

    user = read_user_by_username_from_db(db, username)
    if not user:
        logger.warning(f"User not found for token: username={username}")
        return True  # Consider tokens for non-existent users as revoked

    # Check if the token is in the revoked tokens table
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
    if revoked_token:
        logger.info(f"Token found in revoked tokens table: jti={jti}")
        return True

    # Check if the token was issued before the user's token_blacklist_date
    if user.token_blacklist_date:
        token_iat_datetime = datetime.fromtimestamp(token_iat, tz=timezone.utc)
        if token_iat_datetime < user.token_blacklist_date:
            logger.info(f"Token issued before blacklist date: iat={token_iat_datetime}, blacklist_date={user.token_blacklist_date}")
            return True

    logger.info(f"Token is not revoked: jti={jti}")
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
    """
    current_time = datetime.now(timezone.utc)
    
    for token in active_tokens:
        decoded_token = decode_access_token(token)
        jti = decoded_token.get("jti")
        expires_at = decoded_token.get("exp")

        if not jti or not expires_at:
            continue  # Skip invalid tokens

        # Check if the token is already revoked
        existing_revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
        if existing_revoked_token:
            existing_revoked_token.revoked_at = current_time
        else:
            create_revoked_token_in_db(db, jti, token, user_id, expires_at)

    db.commit()

def revoke_token(db: Session, token: str):
    """
    Revoke a specific token.

    This function creates a new revoked token entry for the given token.

    Args:
        db (Session): The database session.
        token (str): The token to be revoked.

    Returns:
        None
    """
    decoded_token = decode_access_token(token)
    jti = decoded_token.get("jti")
    username = decoded_token.get("sub")
    expires_at = decoded_token.get("exp")

    if not jti or not username or not expires_at:
        raise ValueError("Invalid token format")

    user = read_user_by_username_from_db(db, username)
    if not user:
        raise ValueError("User not found")

    create_revoked_token_in_db(db, jti, token, user.id, expires_at)

def get_active_tokens_for_user(db: Session, user_id: int):
    """
    Get all active (non-revoked) tokens for a given user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose tokens should be retrieved.

    Returns:
        list: A list of active RevokedTokenModel objects for the user.
    """
    current_time = datetime.now(timezone.utc)
    return db.query(RevokedTokenModel).filter(
        RevokedTokenModel.user_id == user_id,
        RevokedTokenModel.expires_at > current_time,
        RevokedTokenModel.revoked_at.is_(None)
    ).all()
