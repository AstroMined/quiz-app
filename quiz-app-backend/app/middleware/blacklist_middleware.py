# filename: app/middleware/blacklist_middleware.py

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings_core
from app.db.session import get_db
from app.models.authentication import RevokedTokenModel
from app.services.logging_service import logger


async def check_revoked_tokens(request: Request, call_next):
    logger.debug("check_revoked_tokens - Requested URL: %s", request.url.path)
    if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
        logger.debug("check_revoked_tokens - Unprotected endpoint, skipping blacklist check")
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        logger.debug("check_revoked_tokens - Token: %s", token)
        db = next(get_db())
        try:
            revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
            if revoked_token:
                logger.debug("check_revoked_tokens - Token is revoked")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
            logger.debug("check_revoked_tokens - Token is not revoked")
        except Exception as e:
            logger.error("check_revoked_tokens - Error during DB query: %s", e)
        finally:
            db.close()
            logger.debug("check_revoked_tokens - DB session closed")
    
    logger.debug("check_revoked_tokens - Before calling next middleware or endpoint")
    response = await call_next(request)
    logger.debug("check_revoked_tokens - After calling next middleware or endpoint")
    return response

class BlacklistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug("BlacklistMiddleware - Requested URL: %s", request.url.path)
        response = await check_revoked_tokens(request, call_next)
        logger.debug("BlacklistMiddleware - After calling check_revoked_tokens")
        return response
