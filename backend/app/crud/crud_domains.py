# filename: backend/app/crud/crud_domains.py

"""
This module handles CRUD operations for domains in the database.

It provides functions for creating, reading, updating, and deleting domains,
as well as managing associations between domains and disciplines.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models.associations: For DomainToDisciplineAssociation
- backend.app.models.disciplines: For the DisciplineModel
- backend.app.models.domains: For the DomainModel

Main functions:
- create_domain_in_db: Creates a new domain
- read_domain_from_db: Retrieves a single domain by ID
- read_domain_by_name_from_db: Retrieves a single domain by name
- read_domains_from_db: Retrieves multiple domains with pagination
- update_domain_in_db: Updates an existing domain
- delete_domain_from_db: Deletes a domain
- create_domain_to_discipline_association_in_db: Associates a domain with a discipline
- delete_domain_to_discipline_association_from_db: Removes a domain-discipline association
- read_disciplines_for_domain_from_db: Retrieves disciplines for a domain

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_domains import create_domain_in_db

    def add_new_domain(db: Session, name: str, discipline_ids: List[int]):
        domain_data = {"name": name, "discipline_ids": discipline_ids}
        return create_domain_in_db(db, domain_data)
"""

from typing import Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.associations import DomainToDisciplineAssociation
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.services.logging_service import logger


def create_domain_in_db(db: Session, domain_data: Dict) -> DomainModel:
    """
    Create a new domain in the database.

    Args:
        db (Session): The database session.
        domain_data (Dict): A dictionary containing the domain data.
            Required keys: "name"
            Optional keys: "discipline_ids"

    Returns:
        DomainModel: The created domain database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        domain_data = {
            "name": "Natural Sciences",
            "discipline_ids": [1, 2, 3]
        }
        new_domain = create_domain_in_db(db, domain_data)
    """
    db_domain = DomainModel(name=domain_data["name"])
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)

    if "discipline_ids" in domain_data and domain_data["discipline_ids"]:
        for discipline_id in domain_data["discipline_ids"]:
            create_domain_to_discipline_association_in_db(
                db, db_domain.id, discipline_id
            )

    return db_domain


def read_domain_from_db(db: Session, domain_id: int) -> Optional[DomainModel]:
    """
    Retrieve a single domain from the database by its ID.

    Args:
        db (Session): The database session.
        domain_id (int): The ID of the domain to retrieve.

    Returns:
        Optional[DomainModel]: The retrieved domain database object,
        or None if not found.

    Usage example:
        domain = read_domain_from_db(db, 1)
        if domain:
            print(f"Domain name: {domain.name}")
    """
    return db.query(DomainModel).filter(DomainModel.id == domain_id).first()


def read_domain_by_name_from_db(db: Session, name: str) -> Optional[DomainModel]:
    """
    Retrieve a single domain from the database by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the domain to retrieve.

    Returns:
        Optional[DomainModel]: The retrieved domain database object,
        or None if not found.

    Usage example:
        domain = read_domain_by_name_from_db(db, "Natural Sciences")
        if domain:
            print(f"Domain ID: {domain.id}")
    """
    return db.query(DomainModel).filter(DomainModel.name == name).first()


def read_domains_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[DomainModel]:
    """
    Retrieve a list of domains from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[DomainModel]: A list of retrieved domain database objects.

    Usage example:
        domains = read_domains_from_db(db, skip=10, limit=20)
        for domain in domains:
            print(f"Domain: {domain.name}")
    """
    return db.query(DomainModel).offset(skip).limit(limit).all()


def update_domain_in_db(
    db: Session, domain_id: int, domain_data: Dict
) -> Optional[DomainModel]:
    """
    Update an existing domain in the database.

    Args:
        db (Session): The database session.
        domain_id (int): The ID of the domain to update.
        domain_data (Dict): A dictionary containing the updated domain data.

    Returns:
        Optional[DomainModel]: The updated domain database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"name": "Updated Domain Name"}
        updated_domain = update_domain_in_db(db, 1, updated_data)
        if updated_domain:
            print(f"Updated domain name: {updated_domain.name}")
    """
    db_domain = read_domain_from_db(db, domain_id)
    if db_domain:
        for key, value in domain_data.items():
            setattr(db_domain, key, value)
        db.commit()
        db.refresh(db_domain)
    return db_domain


def delete_domain_from_db(db: Session, domain_id: int) -> bool:
    """
    Delete a domain from the database.

    Args:
        db (Session): The database session.
        domain_id (int): The ID of the domain to delete.

    Returns:
        bool: True if the domain was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_domain_from_db(db, 1):
            print("Domain successfully deleted")
        else:
            print("Domain not found or couldn't be deleted")
    """
    db_domain = read_domain_from_db(db, domain_id)
    if db_domain:
        db.delete(db_domain)
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
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error creating domain-discipline association: %s", str(e))
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


def read_disciplines_for_domain_from_db(
    db: Session, domain_id: int
) -> List[DisciplineModel]:
    """
    Retrieve all disciplines associated with a specific domain from the database.

    Args:
        db (Session): The database session.
        domain_id (int): The ID of the domain.

    Returns:
        List[DisciplineModel]: A list of discipline database objects associated with the domain.

    Usage example:
        disciplines = read_disciplines_for_domain_from_db(db, 1)
        for discipline in disciplines:
            print(f"Discipline for domain 1: {discipline.name}")
    """
    return (
        db.query(DisciplineModel)
        .join(DomainToDisciplineAssociation)
        .filter(DomainToDisciplineAssociation.domain_id == domain_id)
        .all()
    )
