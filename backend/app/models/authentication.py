# filename: backend/app/models/authentication.py

from sqlalchemy import Column, DateTime, Integer, String
from datetime import datetime, timezone

from backend.app.db.base import Base


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String(36), primary_key=True, unique=True, nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<RevokedTokenModel(jti='{self.jti}', user_id='{self.user_id}', revoked_at='{self.revoked_at}')>"
