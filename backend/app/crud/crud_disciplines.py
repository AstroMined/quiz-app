# filename: backend/app/crud/crud_disciplines.py

"""
This module handles CRUD operations for disciplines in the database.

It provides functions for creating, reading, updating, and deleting disciplines,
as well as managing associations between disciplines, domains, and subjects.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models.associations: DisciplineToSubjectAssociation and DomainToDisciplineAssociation
- backend.app.models.disciplines: For the DisciplineModel
- backend.app.models.domains: For the DomainModel
- backend.app.models.subjects: For the SubjectModel

Main functions:
- create_discipline_in_db: Creates a new discipline
- read_discipline_from_db: Retrieves a single discipline by ID
- read_discipline_by_name_from_db: Retrieves a single discipline by name
- read_disciplines_from_db: Retrieves multiple disciplines with pagination
- update_discipline_in_db: Updates an existing discipline
- delete_discipline_from_db: Deletes a discipline
- create_domain_to_discipline_association_in_db: Associates a domain with a discipline
- delete_domain_to_discipline_association_from_db: Removes a domain-discipline association
- create_discipline_to_subject_association_in_db: Associates a discipline with a subject
- delete_discipline_to_subject_association_from_db: Removes a discipline-subject association
- read_domains_for_discipline_from_db: Retrieves domains for a discipline
- read_subjects_for_discipline_from_db: Retrieves subjects for a discipline

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_disciplines import create_discipline_in_db

    def add_new_discipline(db: Session, name: str, domain_ids: List[int], subject_ids: List[int]):
        discipline_data = {"name": name, "domain_ids": domain_ids, "subject_ids": subject_ids}
        return create_discipline_in_db(db, discipline_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import (
    DisciplineToSubjectAssociation,
    DomainToDisciplineAssociation,
)
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.models.subjects import SubjectModel
from backend.app.services.logging_service import logger


def create_discipline_in_db(db: Session, discipline_data: Dict) -> DisciplineModel:
    """
    Create a new discipline in the database.

    Args:
        db (Session): The database session.
        discipline_data (Dict): A dictionary containing the discipline data.
            Required keys: "name"
            Optional keys: "domain_ids", "subject_ids"

    Returns:
        DisciplineModel: The created discipline database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        discipline_data = {
            "name": "Physics",
            "domain_ids": [1, 2],
            "subject_ids": [3, 4, 5]
        }
        new_discipline = create_discipline_in_db(db, discipline_data)
    """
    db_discipline = DisciplineModel(name=discipline_data["name"])
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)

    if "domain_ids" in discipline_data and discipline_data["domain_ids"]:
        for domain_id in discipline_data["domain_ids"]:
            create_domain_to_discipline_association_in_db(
                db, domain_id, db_discipline.id
            )

    if "subject_ids" in discipline_data and discipline_data["subject_ids"]:
        for subject_id in discipline_data["subject_ids"]:
            create_discipline_to_subject_association_in_db(
                db, db_discipline.id, subject_id
            )

    return db_discipline


def read_discipline_from_db(
    db: Session, discipline_id: int
) -> Optional[DisciplineModel]:
    """
    Retrieve a single discipline from the database by its ID.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline to retrieve.

    Returns:
        Optional[DisciplineModel]: The retrieved discipline database object,
        or None if not found.

    Usage example:
        discipline = read_discipline_from_db(db, 1)
        if discipline:
            print(f"Discipline name: {discipline.name}")
    """
    return db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()


def read_discipline_by_name_from_db(
    db: Session, name: str
) -> Optional[DisciplineModel]:
    """
    Retrieve a single discipline from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the discipline to retrieve.

    Returns:
        Optional[DisciplineModel]: The retrieved discipline database object,
        or None if not found.

    Usage example:
        discipline = read_discipline_by_name_from_db(db, "Physics")
        if discipline:
            print(f"Discipline ID: {discipline.id}")
    """
    return db.query(DisciplineModel).filter(DisciplineModel.name == name).first()


def read_disciplines_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[DisciplineModel]:
    """
    Retrieve a list of disciplines from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[DisciplineModel]: A list of retrieved discipline database objects.

    Usage example:
        disciplines = read_disciplines_from_db(db, skip=10, limit=20)
        for discipline in disciplines:
            print(f"Discipline: {discipline.name}")
    """
    return db.query(DisciplineModel).offset(skip).limit(limit).all()


def update_discipline_in_db(
    db: Session, discipline_id: int, discipline_data: Dict
) -> Optional[DisciplineModel]:
    """
    Update an existing discipline in the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline to update.
        discipline_data (Dict): A dictionary containing the updated discipline data.

    Returns:
        Optional[DisciplineModel]: The updated discipline database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"name": "Updated Discipline Name"}
        updated_discipline = update_discipline_in_db(db, 1, updated_data)
        if updated_discipline:
            print(f"Updated discipline name: {updated_discipline.name}")
    """
    db_discipline = read_discipline_from_db(db, discipline_id)
    if db_discipline:
        for key, value in discipline_data.items():
            setattr(db_discipline, key, value)
        db.commit()
        db.refresh(db_discipline)
    return db_discipline


def delete_discipline_from_db(db: Session, discipline_id: int) -> bool:
    """
    Delete a discipline from the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline to delete.

    Returns:
        bool: True if the discipline was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_discipline_from_db(db, 1):
            print("Discipline successfully deleted")
        else:
            print("Discipline not found or couldn't be deleted")
    """
    db_discipline = read_discipline_from_db(db, discipline_id)
    if db_discipline:
        db.delete(db_discipline)
        db.commit()
        return True
    return False


def create_domain_to_discipline_association_in_db(
    db: Session, domain_id: int, discipline_id: int
) -> bool:
    """
    Create an association between a domain and a discipline in the database.

    Args:
        db (Session): The database session.
        domain_id (int): The ID of the domain.
        discipline_id (int): The ID of the discipline.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_domain_to_discipline_association_in_db(db, 1, 2):
            print("Association created successfully")
        else:
            print("Failed to create association")
    """
    association = DomainToDisciplineAssociation(
        domain_id=domain_id, discipline_id=discipline_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError:
        logger.exception("Error creating domain-discipline association")
        db.rollback()
        return False


def delete_domain_to_discipline_association_from_db(
    db: Session, domain_id: int, discipline_id: int
) -> bool:
    """
    Delete an association between a domain and a discipline from the database.

    Args:
        db (Session): The database session.
        domain_id (int): The ID of the domain.
        discipline_id (int): The ID of the discipline.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_domain_to_discipline_association_from_db(db, 1, 2):
            print("Association deleted successfully")
        else:
            print("Association not found or couldn't be deleted")
    """
    association = (
        db.query(DomainToDisciplineAssociation)
        .filter_by(domain_id=domain_id, discipline_id=discipline_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def create_discipline_to_subject_association_in_db(
    db: Session, discipline_id: int, subject_id: int
) -> bool:
    """
    Create an association between a discipline and a subject in the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline.
        subject_id (int): The ID of the subject.

    Returns:
        bool: True if the association was successfully created, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if create_discipline_to_subject_association_in_db(db, 1, 2):
            print("Association created successfully")
        else:
            print("Failed to create association")
    """
    association = DisciplineToSubjectAssociation(
        discipline_id=discipline_id, subject_id=subject_id
    )
    db.add(association)
    try:
        db.commit()
        return True
    except SQLAlchemyError:
        logger.exception("Error creating discipline-subject association")
        db.rollback()
        return False


def delete_discipline_to_subject_association_from_db(
    db: Session, discipline_id: int, subject_id: int
) -> bool:
    """
    Delete an association between a discipline and a subject from the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline.
        subject_id (int): The ID of the subject.

    Returns:
        bool: True if the association was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_discipline_to_subject_association_from_db(db, 1, 2):
            print("Association deleted successfully")
        else:
            print("Association not found or couldn't be deleted")
    """
    association = (
        db.query(DisciplineToSubjectAssociation)
        .filter_by(discipline_id=discipline_id, subject_id=subject_id)
        .first()
    )
    if association:
        db.delete(association)
        db.commit()
        return True
    return False


def read_domains_for_discipline_from_db(
    db: Session, discipline_id: int
) -> List[DomainModel]:
    """
    Retrieve all domains associated with a specific discipline from the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline.

    Returns:
        List[DomainModel]: A list of domain database objects associated with the discipline.

    Usage example:
        domains = read_domains_for_discipline_from_db(db, 1)
        for domain in domains:
            print(f"Domain for discipline 1: {domain.name}")
    """
    return (
        db.query(DomainModel)
        .join(DomainToDisciplineAssociation)
        .filter(DomainToDisciplineAssociation.discipline_id == discipline_id)
        .all()
    )


def read_subjects_for_discipline_from_db(
    db: Session, discipline_id: int
) -> List[SubjectModel]:
    """
    Retrieve all subjects associated with a specific discipline from the database.

    Args:
        db (Session): The database session.
        discipline_id (int): The ID of the discipline.

    Returns:
        List[SubjectModel]: A list of subject database objects associated with the discipline.

    Usage example:
        subjects = read_subjects_for_discipline_from_db(db, 1)
        for subject in subjects:
            print(f"Subject for discipline 1: {subject.name}")
    """
    return (
        db.query(SubjectModel)
        .join(DisciplineToSubjectAssociation)
        .filter(DisciplineToSubjectAssociation.discipline_id == discipline_id)
        .all()
    )
