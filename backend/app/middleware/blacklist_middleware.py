# filename: backend/app/middleware/blacklist_middleware.py

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import ExpiredSignatureError

from backend.app.core.config import settings_core
from backend.app.core.jwt import decode_access_token
from backend.app.crud.authentication import is_token_revoked
from backend.app.db.session import get_db
from backend.app.services.logging_service import logger


class BlacklistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_db_func=None):
        super().__init__(app)
        self.get_db_func = get_db_func or get_db

    async def dispatch(self, request: Request, call_next):
        logger.debug(f"BlacklistMiddleware: Processing request to {request.url.path}")

        # Allow unprotected endpoints to pass through without token validation
        if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
            logger.debug(
                f"BlacklistMiddleware: Allowing unprotected endpoint {request.url.path} to pass through"
            )
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                scheme, token = authorization.split()
                if scheme.lower() != "bearer":
                    logger.warning("BlacklistMiddleware: Invalid authentication scheme")
                    raise HTTPException(
                        status_code=401, detail="Invalid authentication scheme"
                    )

                # Use injected database function (supports test overrides)
                db = next(self.get_db_func())
                try:
                    if is_token_revoked(db, token):
                        logger.warning("BlacklistMiddleware: Token has been revoked")
                        raise HTTPException(
                            status_code=401, detail="Token has been revoked"
                        )
                except ExpiredSignatureError:
                    logger.warning("BlacklistMiddleware: Token has expired")
                    raise HTTPException(
                        status_code=401, detail="Token has expired"
                    )
                finally:
                    db.close()

                logger.debug("BlacklistMiddleware: Token is valid")
            except HTTPException as e:
                logger.error(f"BlacklistMiddleware: HTTPException - {e.detail}")
                return JSONResponse(
                    status_code=e.status_code, content={"detail": e.detail}
                )
            except Exception as e:
                logger.error(f"BlacklistMiddleware: Unexpected error - {str(e)}")
                return JSONResponse(status_code=401, content={"detail": str(e)})
        else:
            logger.debug("BlacklistMiddleware: No Authorization header present")

        response = await call_next(request)
        return response
