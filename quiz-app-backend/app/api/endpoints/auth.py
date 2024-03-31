# filename: app/api/endpoints/auth.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core import create_access_token, verify_password
from app.db import get_db
from app.models import User, RevokedToken
from app.schemas import Token, LoginForm

logger = logging.getLogger(__name__)

router = APIRouter()

blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: LoginForm, db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and generate an access token.
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if user:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Endpoint to logout the current user and invalidate the access token.
    
    Args:
        token (str): The access token to be invalidated.
        db (Session): The database session.
        
    Returns:
        dict: A success message indicating the user has been logged out.
        
    Raises:
        HTTPException: If an error occurs during token decoding or user logout.
    """
    try:
        # Check if the token is already revoked
        revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
        if revoked_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token has been revoked")

        # Revoke the token
        revoked_token = RevokedToken(token=token)
        db.add(revoked_token)
        db.commit()
        return {"message": "Successfully logged out"}

    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token") from exc
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to logout user") from exc
