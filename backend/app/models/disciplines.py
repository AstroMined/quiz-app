# filename: backend/app/models/disciplines.py

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class DisciplineModel(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    domains = relationship("DomainModel", secondary="domain_to_discipline_association", back_populates="disciplines")
    subjects = relationship("SubjectModel", secondary="discipline_to_subject_association", back_populates="disciplines")

    def __repr__(self):
        return f"<Discipline(id={self.id}, name='{self.name}')>"
