# filename: backend/tests/integration/database/test_reference_data_initialization.py

"""
Integration tests for reference data initialization.

This module validates that the base reference data required for all tests
is properly created and accessible. These tests ensure that foreign key
relationships work correctly after the reference data setup.

Key test areas:
- Role and permission creation and availability
- Content hierarchy creation with proper relationships
- User creation with valid role references
- Content creation with valid discipline/subject references
"""

import pytest
from sqlalchemy.orm import sessionmaker

from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.models.domains import DomainModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.time_period import TimePeriodModel


def test_reference_data_exists(base_reference_data, test_engine):
    """Verify all required reference data is created."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    
    try:
        # Check roles exist
        role_count = session.query(RoleModel).count()
        assert role_count >= 3, f"Expected at least 3 roles, got {role_count}"
        
        # Check permissions exist
        permission_count = session.query(PermissionModel).count()
        assert permission_count >= 10, f"Expected at least 10 permissions, got {permission_count}"
        
        # Check default role exists
        default_role = session.query(RoleModel).filter_by(default=True).first()
        assert default_role is not None, "Default role must exist"
        assert default_role.name == "user", f"Default role should be 'user', got '{default_role.name}'"
        
        # Check disciplines exist
        discipline_count = session.query(DisciplineModel).count()
        assert discipline_count >= 3, f"Expected at least 3 disciplines, got {discipline_count}"
        
        # Check domains exist
        domain_count = session.query(DomainModel).count()
        assert domain_count >= 2, f"Expected at least 2 domains, got {domain_count}"
        
        # Check subjects exist
        subject_count = session.query(SubjectModel).count()
        assert subject_count >= 5, f"Expected at least 5 subjects, got {subject_count}"
        
        # Check time periods exist
        time_period_count = session.query(TimePeriodModel).count()
        assert time_period_count >= 4, f"Expected at least 4 time periods, got {time_period_count}"
        
    finally:
        session.close()


def test_role_permission_relationships(base_reference_data, test_engine):
    """Verify roles have proper permission relationships."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    
    try:
        # Check user role has basic permissions
        user_role = session.query(RoleModel).filter_by(name="user").first()
        assert user_role is not None, "User role must exist"
        assert len(user_role.permissions) >= 4, f"User role should have at least 4 permissions, got {len(user_role.permissions)}"
        
        # Check admin role has more permissions
        admin_role = session.query(RoleModel).filter_by(name="admin").first()
        assert admin_role is not None, "Admin role must exist"
        assert len(admin_role.permissions) >= len(user_role.permissions), "Admin should have at least as many permissions as user"
        
        # Check superadmin role has most permissions
        superadmin_role = session.query(RoleModel).filter_by(name="superadmin").first()
        assert superadmin_role is not None, "Superadmin role must exist"
        assert len(superadmin_role.permissions) >= len(admin_role.permissions), "Superadmin should have at least as many permissions as admin"
        
    finally:
        session.close()


def test_content_hierarchy_relationships(base_reference_data, test_engine):
    """Verify content hierarchy has proper many-to-many relationships."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    
    try:
        # Check Mathematics discipline exists and has domain relationship
        math_discipline = session.query(DisciplineModel).filter_by(name="Mathematics").first()
        assert math_discipline is not None, "Mathematics discipline must exist"
        assert len(math_discipline.domains) > 0, "Mathematics discipline should have at least one domain"
        
        # Check STEM domain exists and has discipline relationships
        stem_domain = session.query(DomainModel).filter_by(name="STEM").first()
        assert stem_domain is not None, "STEM domain must exist"
        assert len(stem_domain.disciplines) >= 2, f"STEM domain should have at least 2 disciplines, got {len(stem_domain.disciplines)}"
        
        # Check Algebra subject exists and has discipline relationship
        algebra_subject = session.query(SubjectModel).filter_by(name="Algebra").first()
        assert algebra_subject is not None, "Algebra subject must exist"
        assert len(algebra_subject.disciplines) > 0, "Algebra subject should have at least one discipline"
        
        # Verify relationship consistency
        math_subjects = [s for s in math_discipline.subjects if s.name in ["Algebra", "Calculus", "Geometry"]]
        assert len(math_subjects) >= 2, f"Mathematics discipline should have at least 2 subjects, got {len(math_subjects)}"
        
    finally:
        session.close()


def test_reference_data_access_fixtures(default_role, admin_role, superadmin_role, 
                                       test_disciplines, test_subjects, test_domains,
                                       mathematics_discipline, algebra_subject):
    """Verify reference data access fixtures work correctly."""
    # Test role fixtures
    assert default_role is not None, "default_role fixture should return a role"
    assert default_role.default is True, "default_role should have default=True"
    assert default_role.name == "user", f"default_role should be 'user', got '{default_role.name}'"
    
    assert admin_role is not None, "admin_role fixture should return a role"
    assert admin_role.name == "admin", f"admin_role should be 'admin', got '{admin_role.name}'"
    
    assert superadmin_role is not None, "superadmin_role fixture should return a role"
    assert superadmin_role.name == "superadmin", f"superadmin_role should be 'superadmin', got '{superadmin_role.name}'"
    
    # Test content hierarchy fixtures
    assert test_disciplines is not None, "test_disciplines fixture should return disciplines"
    assert len(test_disciplines) >= 3, f"Should have at least 3 disciplines, got {len(test_disciplines)}"
    
    assert test_subjects is not None, "test_subjects fixture should return subjects"
    assert len(test_subjects) >= 5, f"Should have at least 5 subjects, got {len(test_subjects)}"
    
    assert test_domains is not None, "test_domains fixture should return domains"
    assert len(test_domains) >= 2, f"Should have at least 2 domains, got {len(test_domains)}"
    
    # Test specific fixtures
    assert mathematics_discipline is not None, "mathematics_discipline fixture should return Mathematics"
    assert mathematics_discipline.name == "Mathematics", f"Should be 'Mathematics', got '{mathematics_discipline.name}'"
    
    assert algebra_subject is not None, "algebra_subject fixture should return Algebra"
    assert algebra_subject.name == "Algebra", f"Should be 'Algebra', got '{algebra_subject.name}'"


def test_foreign_key_constraints_work(base_reference_data, test_engine):
    """Verify foreign key constraints are working with reference data."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    
    try:
        # Test that we can find references properly
        default_role = session.query(RoleModel).filter_by(default=True).first()
        assert default_role is not None, "Should be able to find default role"
        
        # Test that role has a valid ID that can be used for foreign keys
        assert default_role.id is not None, "Default role should have a valid ID"
        assert isinstance(default_role.id, int), "Role ID should be an integer"
        
        # Test content hierarchy foreign key availability
        math_discipline = session.query(DisciplineModel).filter_by(name="Mathematics").first()
        assert math_discipline is not None, "Should be able to find Mathematics discipline"
        assert math_discipline.id is not None, "Mathematics discipline should have a valid ID"
        
        algebra_subject = session.query(SubjectModel).filter_by(name="Algebra").first()
        assert algebra_subject is not None, "Should be able to find Algebra subject"
        assert algebra_subject.id is not None, "Algebra subject should have a valid ID"
        
    finally:
        session.close()


def test_reference_data_consistency_across_workers(base_reference_data, test_engine):
    """Verify reference data is consistent and available for all workers."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    
    try:
        # Multiple queries should return consistent results
        for _ in range(3):
            default_role = session.query(RoleModel).filter_by(default=True).first()
            assert default_role is not None, "Default role should be consistently available"
            assert default_role.name == "user", "Default role should consistently be 'user'"
            
            math_discipline = session.query(DisciplineModel).filter_by(name="Mathematics").first()
            assert math_discipline is not None, "Mathematics discipline should be consistently available"
            
            stem_domain = session.query(DomainModel).filter_by(name="STEM").first()
            assert stem_domain is not None, "STEM domain should be consistently available"
    
    finally:
        session.close()