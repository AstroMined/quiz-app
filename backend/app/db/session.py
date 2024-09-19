# filename: backend/app/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool

from backend.app.core.config import settings_core
from backend.app.db.base import Base
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.services.logging_service import logger

# Determine the environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

# Set pool settings based on the environment
if ENVIRONMENT == "test":
    # For SQLite (testing), use a smaller pool
    pool_settings = {
        "poolclass": QueuePool,
        "pool_size": 30,
        "max_overflow": 40,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    }
elif ENVIRONMENT in ["dev", "prod"]:
    # For MariaDB (production), use a larger pool
    pool_settings = {
        "poolclass": QueuePool,
        "pool_size": 50,
        "max_overflow": 100,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    }
else:
    # For unknown environments, use NullPool as a safe default
    pool_settings = {"poolclass": NullPool}

# Create the engine with the appropriate pool settings
engine = create_engine(settings_core.DATABASE_URL, **pool_settings)

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

# Add logging for connection pool statistics
def log_pool_info():
    if hasattr(engine.pool, "size"):
        logger.info(f"Database connection pool status:")
        logger.info(f"  Pool size: {engine.pool.size()}")
        logger.info(f"  Connections in use: {engine.pool.checkedin()}")
        logger.info(f"  Connections available: {engine.pool.checkedout()}")
    else:
        logger.info("Database is not using a connection pool.")

# You can call this function periodically or in strategic places in your application
# For example, you might want to add it to your main FastAPI app startup event
# @app.on_event("startup")
# async def startup_event():
#     log_pool_info()
