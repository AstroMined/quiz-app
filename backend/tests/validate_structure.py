#!/usr/bin/env python3
"""Validate test structure follows CLAUDE.md guidelines."""

import os
import subprocess
from pathlib import Path


def validate_test_structure():
    """Validate the test directory structure."""
    test_dir = Path(__file__).parent
    
    # Check required directories exist
    required_dirs = [
        "unit/models", "unit/schemas", "unit/services", "unit/utils",
        "integration/crud", "integration/api", "integration/models", 
        "integration/services", "integration/workflows", "integration/database"
    ]
    
    for dir_path in required_dirs:
        full_path = test_dir / dir_path
        assert full_path.exists(), f"Required directory missing: {dir_path}"
        assert (full_path / "__init__.py").exists(), f"Missing __init__.py in {dir_path}"
    
    # Check old directories are removed
    old_dirs = ["test_models", "test_schemas", "test_api", "test_crud", "test_services", "test_core", "test_db", "test_integration"]
    for old_dir in old_dirs:
        old_path = test_dir / old_dir
        assert not old_path.exists(), f"Old directory still exists: {old_dir}"
    
    print("✅ Test structure validation passed!")


def validate_test_separation():
    """Validate unit/integration test separation."""
    test_dir = Path(__file__).parent
    
    # Check unit tests don't use database
    unit_files = list((test_dir / "unit").rglob("*.py"))
    for file_path in unit_files:
        if file_path.name.startswith("test_"):
            content = file_path.read_text()
            assert "db_session" not in content, f"Unit test uses db_session: {file_path}"
    
    # Check integration tests use database appropriately  
    integration_files = list((test_dir / "integration").rglob("*.py"))
    integration_with_db = []
    for file_path in integration_files:
        if file_path.name.startswith("test_"):
            content = file_path.read_text()
            if "db_session" in content:
                integration_with_db.append(file_path)
    
    assert len(integration_with_db) > 0, "No integration tests found using database"
    print(f"✅ Test separation validation passed! {len(integration_with_db)} integration tests use database.")


if __name__ == "__main__":
    validate_test_structure()
    validate_test_separation()
    print("🎉 All validations passed! Test refactoring is complete.")