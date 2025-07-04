# app/services/permission_generator_service.py

from fastapi import FastAPI

from backend.app.core.config import settings_core
from backend.app.models.permissions import PermissionModel


def generate_permissions(app: FastAPI):
    permissions = set()
    method_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete",
    }

    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                if method in method_map:
                    path = (
                        route.path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                    )
                    if path not in settings_core.UNPROTECTED_ENDPOINTS:
                        permission = f"{method_map[method]}_{path}"
                        permissions.add(permission)

    return permissions


def ensure_permissions_in_db(db, permissions):
    existing_permissions = set(p.name for p in db.query(PermissionModel).all())
    new_permissions = permissions - existing_permissions

    for permission in new_permissions:
        db.add(PermissionModel(name=permission))

    db.commit()
