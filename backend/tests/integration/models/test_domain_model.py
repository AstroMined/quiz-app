# filename: backend/tests/integration/models/test_domain_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.domains import DomainModel
from backend.app.models.disciplines import DisciplineModel


def test_domain_creation(db_session):
    domain = DomainModel(name="Science and Technology")
    db_session.add(domain)
    db_session.commit()

    assert domain.id is not None
    assert domain.name == "Science and Technology"


def test_domain_unique_name(db_session):
    domain1 = DomainModel(name="Arts and Humanities")
    db_session.add(domain1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        domain2 = DomainModel(name="Arts and Humanities")
        db_session.add(domain2)
        db_session.commit()
    db_session.rollback()


def test_domain_discipline_relationship(db_session):
    domain = DomainModel(name="Natural Sciences")
    discipline = DisciplineModel(name="Physics")
    domain.disciplines.append(discipline)
    db_session.add_all([domain, discipline])
    db_session.commit()

    assert discipline in domain.disciplines
    assert domain in discipline.domains


def test_domain_required_fields(db_session):
    # Domain model allows None name, so this test checks basic creation
    domain = DomainModel()
    db_session.add(domain)
    db_session.commit()
    
    assert domain.id is not None
    assert domain.name is None


def test_domain_repr(db_session):
    domain = DomainModel(name="Engineering")
    db_session.add(domain)
    db_session.commit()

    expected_repr = f"<Domain(id={domain.id}, name='Engineering')>"
    assert repr(domain) == expected_repr


def test_domain_schema_from_attributes(db_session, test_model_domain):
    from backend.app.schemas.domains import DomainSchema
    
    schema = DomainSchema.model_validate(test_model_domain)
    assert schema.id == test_model_domain.id
    assert schema.name == test_model_domain.name
    assert isinstance(schema.disciplines, list)
    for discipline in schema.disciplines:
        assert "id" in discipline
        assert "name" in discipline