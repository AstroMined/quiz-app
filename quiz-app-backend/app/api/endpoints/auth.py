# filename: app/api/endpoints/auth.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core import create_access_token, verify_password
from app.db import get_db
from app.models import UserModel, RevokedTokenModel
from app.schemas import TokenSchema, LoginFormSchema

logger = logging.getLogger(__name__)

router = APIRouter()

blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login", response_model=TokenSchema)
async def login_for_access_token(form_data: LoginFormSchema, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()

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
