from sqlalchemy import Column, Integer, String, DateTime
from app.db.base_class import Base
from datetime import datetime

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
