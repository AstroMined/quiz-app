# filename: app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings_core
from app.db.base import Base
from app.models.permissions import PermissionModel
from app.models.roles import RoleModel
from app.services.logging_service import logger

engine = create_engine(settings_core.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Import all the models here to ensure they are registered with SQLAlchemy
    db = SessionLocal()
    try:
        # Add default roles
        superadmin_permissions = db.query(PermissionModel).all()
        superadmin_role = RoleModel(name="superadmin", description="Super Administrator", permissions=superadmin_permissions, default=False)
        logger.debug("Superadmin role: %s", superadmin_role)
        
        user_permissions = db.query(PermissionModel).filter(
            PermissionModel.name.in_([
                'read__docs', 'read__redoc', 'read__openapi.json', 'read__',
                'create__login', 'create__register_', 'read__users_me', 'update__users_me'
            ])
        ).all()
        user_role = RoleModel(name="user", description="Regular User", permissions=user_permissions, default=True)
        logger.debug("User role: %s", user_role)

        db.add_all([superadmin_role, user_role])
        db.commit()
    finally:
        db.close()

    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
