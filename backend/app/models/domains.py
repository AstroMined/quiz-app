# filename: backend/app/models/domains.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class DomainModel(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    disciplines = relationship(
        "DisciplineModel",
        secondary="domain_to_discipline_association",
        back_populates="domains",
    )

    def __repr__(self):
        return f"<Domain(id={self.id}, name='{self.name}')>"
