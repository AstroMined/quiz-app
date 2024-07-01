# app/services/permission_generator_service.py

from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.core.config import settings_core
from app.services.logging_service import logger
from app.models.permissions import PermissionModel

def generate_permissions(app: FastAPI, db: Session):
    permissions = []
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
                    path = route.path.replace("/", "_").replace("{", "").replace("}", "")
                    if path not in settings_core.UNPROTECTED_ENDPOINTS:
                        permission = f"{method_map[method]}_{path}"
                        permissions.append(permission)
                        logger.debug("Generated permission: %s", permission)



    # Check if the generated permissions exist in the database and add them if they don't
    for permission in permissions:
        db_permission = db.query(PermissionModel).filter(PermissionModel.name == permission).first()
        if not db_permission:
            logger.debug("Adding permission to the database: %s", permission)
            db_permission = PermissionModel(name=permission)
            db.add(db_permission)

    # Delete permissions from the database that are not in the generated list
    db_permissions = db.query(PermissionModel).all()
    for db_permission in db_permissions:
        if db_permission.name not in permissions:
            logger.debug("Deleting permission from the database: %s", db_permission.name)
            db.delete(db_permission)

    db.commit()

    return set(permissions)
