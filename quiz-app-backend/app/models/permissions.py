# filename: app/models/permissions.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.associations import RoleToPermissionAssociation

class PermissionModel(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    roles = relationship(
        "RoleModel",
        secondary=RoleToPermissionAssociation.__tablename__,
        back_populates="permissions"
    )

    def __repr__(self):
        return f"<PermissionModel(id={self.id}, name='{self.name}')>"
