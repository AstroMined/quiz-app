# filename: backend/app/api/endpoints/authentication.py

"""
Authentication API

This module provides API endpoints for user authentication in the quiz application.
It includes operations for user login, logout, and logging out all sessions.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations and uses JWT for token-based authentication.

Endpoints:
- POST /login: Authenticate a user and return an access token
- POST /logout: Logout a user by revoking their access token
- POST /logout/all: Logout all sessions for a user by revoking all their access tokens

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency for the logout endpoints.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.core.jwt import create_access_token, decode_access_token
from backend.app.db.session import get_db
from backend.app.schemas.authentication import TokenSchema, LoginFormSchema
from backend.app.services.authentication_service import authenticate_user
from backend.app.services.user_service import oauth2_scheme
from backend.app.services.auth_utils import check_auth_status
from backend.app.crud.authentication import is_token_revoked, revoke_token
from backend.app.crud.crud_user import update_user_token_blacklist_date, read_user_by_username_from_db
from backend.app.services.logging_service import logger

router = APIRouter()

@router.post("/login", response_model=TokenSchema)
async def login_endpoint(
    form_data: LoginFormSchema,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.

    This endpoint allows users to login by providing their username and password.
    If credentials are valid, returns an access token for use in subsequent authenticated requests.

    Args:
        form_data (LoginFormSchema): The login form data containing username, password, and remember_me flag.
        db (Session): The database session.

    Returns:
        TokenSchema: An object containing the access token and token type.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the provided credentials are invalid or the user is inactive.
    """
    logger.debug("Login attempt for user: %s", form_data.username)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_active:
        logger.warning(f"Login failed for user: {form_data.username}. User not found or inactive.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("User authenticated successfully: %s", user.username)
    
    # Check if the user's token_blacklist_date is in the past
    current_time = datetime.now(timezone.utc)
    if user.token_blacklist_date:
        logger.debug(f"User {user.username} has token_blacklist_date: {user.token_blacklist_date}")
        if user.token_blacklist_date > current_time:
            logger.warning(f"Login attempt for user with active token blacklist: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="All sessions have been logged out. Please try again later.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            logger.debug(f"Clearing token_blacklist_date for user: {user.username}")
            update_user_token_blacklist_date(db, user.id, None)

    # Set expiration time based on remember_me flag
    # For remember_me tokens, set expiration to 30 days; otherwise, use the default expiration time
    expires_delta = timedelta(days=30) if form_data.remember_me else None
    access_token = create_access_token(data={"sub": user.username, "remember_me": form_data.remember_me}, expires_delta=expires_delta)
    logger.debug("Access token created for user: %s (remember_me: %s)", user.username, form_data.remember_me)
    response = {"access_token": access_token, "token_type": "bearer"}
    logger.debug("Login response: %s", response)
    return response

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_endpoint(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout a user by revoking their access token.

    This endpoint allows authenticated users to logout by revoking their current access token.
    Once revoked, the token can no longer be used for authentication.
    This handles both regular and remember me tokens.

    Args:
        request (Request): The FastAPI request object.
        token (str): The access token to be revoked.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful logout.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the token is invalid or expired.
            - 403 Forbidden: If the user doesn't have sufficient permissions.
            - 500 Internal Server Error: If there's an error during the logout process.
    """
    check_auth_status(request)

    try:
        decoded_token = decode_access_token(token)
        jti = decoded_token.get("jti")
        if not jti:
            raise ValueError("Token does not contain a JTI")

        if is_token_revoked(db, token):
            return {"message": "Token already revoked"}
        
        revoke_token(db, token)
        is_remember_me = decoded_token.get("remember_me", False)
        logger.debug(f"Token revoked for user: {decoded_token.get('sub')} (remember_me: {is_remember_me})")
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout user"
        ) from e

@router.post("/logout/all", status_code=status.HTTP_200_OK)
async def logout_all_sessions_endpoint(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout all sessions for a user by updating their token_blacklist_date.

    This endpoint allows authenticated users to logout from all their active sessions
    by updating their token_blacklist_date, which invalidates all previously issued tokens,
    including remember me tokens.

    Args:
        request (Request): The FastAPI request object.
        token (str): The current access token.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful logout from all sessions.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the token is invalid or expired.
            - 403 Forbidden: If the user doesn't have sufficient permissions.
            - 500 Internal Server Error: If there's an error during the logout process.
    """
    check_auth_status(request)

    try:
        decoded_token = decode_access_token(token)
        username = decoded_token.get("sub")
        if not username:
            raise ValueError("Token does not contain a subject (username)")

        user = read_user_by_username_from_db(db, username)
        if not user:
            raise ValueError("User not found")

        # Update the user's token_blacklist_date to the current time
        current_time = datetime.now(timezone.utc)
        update_user_token_blacklist_date(db, user.id, current_time)
        logger.debug(f"Updated token_blacklist_date for user {username} to {current_time} (all sessions, including remember me)")

        return {"message": "Successfully logged out from all sessions"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout user from all sessions: {str(e)}"
        ) from e
