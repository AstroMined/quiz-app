# backend/app/middleware/authorization_middleware.py

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import settings_core
from backend.app.db.session import get_db
from backend.app.models.permissions import PermissionModel
from backend.app.services.authorization_service import has_permission
from backend.app.services.user_service import get_current_user, oauth2_scheme


class AuthorizationMiddleware(BaseHTTPMiddleware):
    method_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete",
    }

    async def dispatch(self, request: Request, call_next):
        request.state.auth_status = {"is_authorized": True, "error": None}
        request.state.current_user = None

        if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
            return await call_next(request)

        token = await oauth2_scheme(request)
        if not token:
            request.state.auth_status = {
                "is_authorized": False,
                "error": "missing_token",
            }
            return JSONResponse(
                status_code=401, content={"detail": "Not authenticated"}
            )

        try:
            db = next(get_db())

            # Check if the token has been invalidated by the BlacklistMiddleware
            if (
                hasattr(request.state, "auth_status")
                and not request.state.auth_status["is_authorized"]
            ):
                error = request.state.auth_status.get("error", "Unknown error")
                return JSONResponse(
                    status_code=401,
                    content={"detail": f"Authentication failed: {error}"},
                )

            current_user, user_status = await get_current_user(token, db)

            if user_status != "valid":
                request.state.auth_status = {
                    "is_authorized": False,
                    "error": user_status,
                }
                return JSONResponse(
                    status_code=401,
                    content={"detail": f"Authentication failed: {user_status}"},
                )

            request.state.current_user = current_user

            route = request.url.path
            crud_verb = self.method_map.get(request.method)

            if crud_verb:
                required_permission = (
                    db.query(PermissionModel)
                    .filter(
                        PermissionModel.name == f"{crud_verb}_{route.strip('/').replace('/', '_')}"
                    )
                    .first()
                )

                if required_permission:
                    if not has_permission(db, current_user, required_permission.name):
                        request.state.auth_status = {
                            "is_authorized": False,
                            "error": "insufficient_permissions",
                        }
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": "User does not have the required permission"
                            },
                        )

            return await call_next(request)
        except Exception as e:
            request.state.auth_status = {
                "is_authorized": False,
                "error": "internal_error",
            }
            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )
        finally:
            db.close()
