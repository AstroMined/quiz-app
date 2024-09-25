# filename: backend/app/services/auth_utils.py

from fastapi import HTTPException, Request, status

from backend.app.services.logging_service import logger


def check_auth_status(request: Request):
    """
    Check the authentication and authorization status from the request state.
    Raise appropriate HTTP exceptions if there are any issues.
    """
    if not hasattr(request.state, "auth_status"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication status not available",
        )

    auth_status = request.state.auth_status

    if not auth_status["is_authorized"]:
        error = auth_status["error"]
        if error in [
            "invalid_token",
            "token_expired",
            "revoked_token",
            "user_not_found",
            "invalid_token_format",
        ]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {error}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif error == "insufficient_permissions":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have the required permissions",
            )
        elif error == "missing_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected authentication error: {error}",
            )


def get_current_user_or_error(request: Request):
    """
    Get the current user from the request state or raise an appropriate HTTP exception.
    """
    check_auth_status(request)
    if not hasattr(request.state, "current_user") or request.state.current_user is None:
        logger.error("No current user found in request state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.current_user
