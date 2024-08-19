# filename: backend/app/api/endpoints/authentication.py

"""
Authentication API

This module provides API endpoints for user authentication in the quiz application.
It includes operations for user login and logout.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations and uses JWT for token-based authentication.

Endpoints:
- POST /login: Authenticate a user and return an access token
- POST /logout: Logout a user by revoking their access token

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency for the logout endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.jwt import create_access_token
from backend.app.db.session import get_db
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.users import UserModel
from backend.app.schemas.authentication import TokenSchema
from backend.app.services.authentication_service import authenticate_user
from backend.app.services.user_service import get_current_user, oauth2_scheme

router = APIRouter()

@router.post("/login", response_model=TokenSchema)
async def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.

    This endpoint allows users to login by providing their username and password.
    If credentials are valid, returns an access token for use in subsequent authenticated requests.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data containing username and password.
        db (Session): The database session.

    Returns:
        TokenSchema: An object containing the access token and token type.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the provided credentials are invalid or the user is inactive.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_endpoint(
    current_user: UserModel = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout a user by revoking their access token.

    This endpoint allows authenticated users to logout by revoking their current access token.
    Once revoked, the token can no longer be used for authentication.

    Args:
        current_user (UserModel): The authenticated user making the request.
        token (str): The access token to be revoked.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful logout.

    Raises:
        HTTPException: 
            - 500 Internal Server Error: If there's an error during the logout process.
    """
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
    if not revoked_token:
        try:
            revoked_token = RevokedTokenModel(token=token)
            db.add(revoked_token)
            db.commit()
            return {"message": "Successfully logged out"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout user"
            ) from e
    else:
        return {"message": "Token already revoked"}
