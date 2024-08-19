# filename: backend/tests/crud/test_crud_disciplines.py

import pytest

from backend.app.crud.crud_disciplines import (
    create_discipline_in_db, create_discipline_to_subject_association_in_db,
    create_domain_to_discipline_association_in_db, delete_discipline_from_db,
    delete_discipline_to_subject_association_from_db,
    delete_domain_to_discipline_association_from_db,
    read_discipline_by_name_from_db, read_discipline_from_db,
    read_disciplines_from_db, read_domains_for_discipline_from_db,
    read_subjects_for_discipline_from_db, update_discipline_in_db)
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_subjects import create_subject_in_db


def test_create_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    assert discipline.name == test_schema_discipline.name

def test_read_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    read_discipline = read_discipline_from_db(db_session, discipline.id)
    assert read_discipline.id == discipline.id
    assert read_discipline.name == discipline.name

def test_read_discipline_by_name(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    read_discipline = read_discipline_by_name_from_db(db_session, discipline.name)
    assert read_discipline.id == discipline.id
    assert read_discipline.name == discipline.name

def test_read_disciplines(db_session, test_schema_discipline):
    create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    disciplines = read_disciplines_from_db(db_session)
    assert len(disciplines) > 0

def test_update_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    updated_data = {"name": "Updated Discipline"}
    updated_discipline = update_discipline_in_db(db_session, discipline.id, updated_data)
    assert updated_discipline.name == "Updated Discipline"

def test_delete_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    assert delete_discipline_from_db(db_session, discipline.id) is True
    assert read_discipline_from_db(db_session, discipline.id) is None

def test_create_domain_to_discipline_association(db_session, test_schema_discipline, test_schema_domain):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    assert create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id) is True

def test_delete_domain_to_discipline_association(db_session, test_schema_discipline, test_schema_domain):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id)
    assert delete_domain_to_discipline_association_from_db(db_session, domain.id, discipline.id) is True

def test_create_discipline_to_subject_association(db_session, test_schema_discipline, test_schema_subject):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id) is True

def test_delete_discipline_to_subject_association(db_session, test_schema_discipline, test_schema_subject):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id)
    assert delete_discipline_to_subject_association_from_db(db_session, discipline.id, subject.id) is True

def test_read_domains_for_discipline(db_session, test_schema_discipline, test_schema_domain):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id)
    domains = read_domains_for_discipline_from_db(db_session, discipline.id)
    assert len(domains) == 1
    assert domains[0].id == domain.id

def test_read_subjects_for_discipline(db_session, test_schema_discipline, test_schema_subject):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id)
    subjects = read_subjects_for_discipline_from_db(db_session, discipline.id)
    assert len(subjects) == 1
    assert subjects[0].id == subject.id
