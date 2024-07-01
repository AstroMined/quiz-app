# filename: app/models/authentication.py

from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base_class import Base


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    # pylint: disable=not-callable
    revoked_at = Column(DateTime, server_default=func.now())
