import pytest
from pydantic import ValidationError
from app.schemas.filters import FilterParamsSchema


def test_filter_params_schema_invalid_params():
    invalid_data = {
        "subject": "Math",
        "topic": "Algebra",
        "subtopic": "Linear Equations",
        "difficulty": "Easy",
        "tags": ["equations", "solving"],
        "invalid_param": "value"  # Invalid parameter
    }
    
    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(**invalid_data)
    
    assert "Extra inputs are not permitted" in str(exc_info.value)
