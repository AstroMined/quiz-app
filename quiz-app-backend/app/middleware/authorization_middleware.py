# app/middleware/authorization_middleware.py

from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings_core
from app.db.session import get_db
from app.models.permissions import PermissionModel
from app.services.authorization_service import has_permission
from app.services.logging_service import logger
from app.services.user_service import get_current_user, oauth2_scheme


class AuthorizationMiddleware(BaseHTTPMiddleware):
    method_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete",
    }

    async def dispatch(self, request: Request, call_next):
        logger.debug("AuthorizationMiddleware - Requested URL: %s", request.url.path)
        if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
            logger.debug("AuthorizationMiddleware - Unprotected endpoint, skipping authorization")
            response = await call_next(request)
            return response

        logger.debug("AuthorizationMiddleware - Protected endpoint, checking authorization")
        token = await oauth2_scheme(request)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")        
        try:
            db = next(get_db())
            current_user = await get_current_user(token, db)
            logger.debug("Current user: %s", current_user)
            route = request.url.path
            crud_verb = self.method_map.get(request.method)

            if crud_verb:
                logger.debug("AuthorizationMiddleware - CRUD verb: %s", crud_verb)
                required_permission = db.query(PermissionModel).filter(
                    PermissionModel.name == f"{crud_verb}_{route.replace('/', '_')}"
                ).first()

                if required_permission:
                    logger.debug("AuthorizationMiddleware - Required permission: %s", required_permission.name)
                    if not has_permission(db, current_user, required_permission.name):
                        logger.debug("AuthorizationMiddleware - User does not have the required permission")
                        raise HTTPException(status_code=403, detail="User does not have the required permission")
                else:
                    logger.debug("AuthorizationMiddleware - No permission found for the current route and CRUD verb")
            else:
                logger.debug("AuthorizationMiddleware - No CRUD verb found for the current request method")

            logger.debug("AuthorizationMiddleware - Before calling the next middleware or endpoint")
            response = await call_next(request)
            logger.debug("AuthorizationMiddleware - After calling the next middleware or endpoint")
            return response
        except HTTPException as e:
            logger.error("HTTPException occurred: %s", e.detail)
            raise e
        except ValidationError as e:
            logger.error("ValidationError occurred: %s", e.errors())
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()) from e
        except Exception as e:
            logger.exception("Unexpected error: %s", str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e
        finally:
            db.close()
