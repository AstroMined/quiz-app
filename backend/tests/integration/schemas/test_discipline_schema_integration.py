# filename: backend/tests/integration/schemas/test_discipline_schema_integration.py

import pytest

from backend.app.schemas.disciplines import DisciplineSchema


def test_discipline_schema_from_attributes(db_session, mathematics_discipline):
    """Test DisciplineSchema validation with real SQLAlchemy model (integration test)."""
    # Re-attach the model to the current session to avoid DetachedInstanceError
    discipline = db_session.merge(mathematics_discipline)
    
    # Force load relationships to avoid lazy loading issues
    _ = discipline.domains
    _ = discipline.subjects
    
    schema = DisciplineSchema.model_validate(discipline)
    assert schema.id == discipline.id
    assert schema.name == discipline.name
    assert isinstance(schema.domains, list)
    assert isinstance(schema.subjects, list)
    for domain in schema.domains:
        assert "id" in domain
        assert "name" in domain
    for subject in schema.subjects:
        assert "id" in subject
        assert "name" in subject