# filename: backend/tests/crud/test_crud_domains.py

import pytest

from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import (
    create_domain_in_db,
    create_domain_to_discipline_association_in_db,
    delete_domain_from_db,
    delete_domain_to_discipline_association_from_db,
    read_disciplines_for_domain_from_db,
    read_domain_by_name_from_db,
    read_domain_from_db,
    read_domains_from_db,
    update_domain_in_db,
)


def test_create_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    assert domain.name == test_schema_domain.name


def test_read_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    read_domain = read_domain_from_db(db_session, domain.id)
    assert read_domain.id == domain.id
    assert read_domain.name == domain.name


def test_read_domain_by_name(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    read_domain = read_domain_by_name_from_db(db_session, domain.name)
    assert read_domain.id == domain.id
    assert read_domain.name == domain.name


def test_read_domains(db_session, test_schema_domain):
    create_domain_in_db(db_session, test_schema_domain.model_dump())
    domains = read_domains_from_db(db_session)
    assert len(domains) > 0


def test_update_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    updated_data = {"name": "Updated Domain"}
    updated_domain = update_domain_in_db(db_session, domain.id, updated_data)
    assert updated_domain.name == "Updated Domain"


def test_delete_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    assert delete_domain_from_db(db_session, domain.id) is True
    assert read_domain_from_db(db_session, domain.id) is None


def test_create_domain_to_discipline_association(
    db_session, test_schema_domain, test_schema_discipline
):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    discipline = create_discipline_in_db(
        db_session, test_schema_discipline.model_dump()
    )
    assert (
        create_domain_to_discipline_association_in_db(
            db_session, domain.id, discipline.id
        )
        is True
    )


def test_delete_domain_to_discipline_association(
    db_session, test_schema_domain, test_schema_discipline
):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    discipline = create_discipline_in_db(
        db_session, test_schema_discipline.model_dump()
    )
    create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id)
    assert (
        delete_domain_to_discipline_association_from_db(
            db_session, domain.id, discipline.id
        )
        is True
    )


def test_read_disciplines_for_domain(
    db_session, test_schema_domain, test_schema_discipline
):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    discipline = create_discipline_in_db(
        db_session, test_schema_discipline.model_dump()
    )
    create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id)
    disciplines = read_disciplines_for_domain_from_db(db_session, domain.id)
    assert len(disciplines) == 1
    assert disciplines[0].id == discipline.id
