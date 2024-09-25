# filename: backend/tests/test_schemas/test_schemas_time_period.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.time_period import TimePeriodSchema


def test_time_period_schema_valid():
    data = {"id": 1, "name": "daily"}
    schema = TimePeriodSchema(**data)
    assert schema.id == 1
    assert schema.name == "daily"


def test_time_period_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        TimePeriodSchema(id=0, name="daily")
    assert "Input should be greater than 0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        TimePeriodSchema(id=1, name="")
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        TimePeriodSchema(id=1, name="invalid")
    assert "Name must be one of: daily, weekly, monthly, yearly" in str(exc_info.value)


def test_time_period_schema_from_attributes(db_session):
    from backend.app.models.time_period import TimePeriodModel

    time_periods = [
        TimePeriodModel.daily(),
        TimePeriodModel.weekly(),
        TimePeriodModel.monthly(),
        TimePeriodModel.yearly(),
    ]

    for model in time_periods:
        db_session.add(model)
    db_session.commit()

    for model in time_periods:
        schema = TimePeriodSchema.model_validate(model)
        assert schema.id == model.id
        assert schema.name == model.name


def test_time_period_schema_predefined_values():
    daily = TimePeriodSchema(id=1, name="daily")
    assert daily.id == 1
    assert daily.name == "daily"

    weekly = TimePeriodSchema(id=7, name="weekly")
    assert weekly.id == 7
    assert weekly.name == "weekly"

    monthly = TimePeriodSchema(id=30, name="monthly")
    assert monthly.id == 30
    assert monthly.name == "monthly"

    yearly = TimePeriodSchema(id=365, name="yearly")
    assert yearly.id == 365
    assert yearly.name == "yearly"


def test_time_period_schema_invalid_combinations():
    with pytest.raises(ValidationError) as exc_info:
        TimePeriodSchema(id=7, name="daily")
    assert "Invalid combination of id and name. For id 7, name should be weekly" in str(
        exc_info.value
    )

    with pytest.raises(ValidationError) as exc_info:
        TimePeriodSchema(id=1, name="weekly")
    assert "Invalid combination of id and name. For id 1, name should be daily" in str(
        exc_info.value
    )
