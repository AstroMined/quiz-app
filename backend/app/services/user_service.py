# filename: backend/app/services/user_service.py

from datetime import datetime, timezone

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session

from backend.app.core.jwt import decode_access_token
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None, "invalid_token"

        user = read_user_by_username_from_db(db, username)
        if user is None:
            return None, "user_not_found"

        return user, "valid"
    except ExpiredSignatureError:
        return None, "token_expired"
    except JWTError:
        return None, "invalid_token"
    except Exception:
        return None, "internal_error"
