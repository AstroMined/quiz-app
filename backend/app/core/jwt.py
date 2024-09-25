# filename: backend/app/core/jwt.py

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt

from backend.app.core.config import settings_core
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.db.session import get_db


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    db = next(get_db())
    user = read_user_by_username_from_db(db, to_encode["sub"])
    if not user:
        raise ValueError("User not found")

    to_encode.update(
        {
            "exp": expire,
            "jti": str(uuid.uuid4()),  # Add a unique JWT ID
            "iat": datetime.now(timezone.utc),  # Add issued at time
        }
    )
    encoded_jwt = jwt.encode(to_encode, settings_core.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings_core.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": True},
        )

        db = next(get_db())
        user = read_user_by_username_from_db(db, payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        # Check if the token was issued before the user's current token_blacklist_date
        if user and user.token_blacklist_date:
            token_issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            if token_issued_at < user.token_blacklist_date:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                )

        return payload
    except ExpiredSignatureError:
        # Allow ExpiredSignatureError to propagate
        raise
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        ) from e
    except HTTPException as e:
        # Re-raise HTTP exceptions (including our custom "Token has been revoked" exception)
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        ) from e
