# filename: backend/app/models/authentication.py

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from backend.app.db.base import Base


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)  # JWT ID
    token = Column(String(500), unique=True, nullable=False)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<RevokedTokenModel(id={self.id}, jti='{self.jti}', revoked_at='{self.revoked_at}')>"
