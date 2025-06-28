# filename: backend/tests/unit/models/test_time_period_model.py

import pytest

from backend.app.core.config import TimePeriod
from backend.app.models.time_period import TimePeriodModel


def test_time_period_model_create_with_daily():
    """Test TimePeriodModel.create() with DAILY enum."""
    model = TimePeriodModel.create(TimePeriod.DAILY)
    
    assert model.id == 1
    assert model.name == "daily"


def test_time_period_model_create_with_weekly():
    """Test TimePeriodModel.create() with WEEKLY enum."""
    model = TimePeriodModel.create(TimePeriod.WEEKLY)
    
    assert model.id == 7
    assert model.name == "weekly"


def test_time_period_model_create_with_monthly():
    """Test TimePeriodModel.create() with MONTHLY enum."""
    model = TimePeriodModel.create(TimePeriod.MONTHLY)
    
    assert model.id == 30
    assert model.name == "monthly"


def test_time_period_model_create_with_yearly():
    """Test TimePeriodModel.create() with YEARLY enum."""
    model = TimePeriodModel.create(TimePeriod.YEARLY)
    
    assert model.id == 365
    assert model.name == "yearly"


def test_time_period_model_repr():
    """Test TimePeriodModel string representation."""
    model = TimePeriodModel.create(TimePeriod.WEEKLY)
    expected = "<TimePeriodModel(id=7, name='weekly')"
    
    assert repr(model) == expected


def test_time_period_model_manual_creation():
    """Test TimePeriodModel creation with manual values."""
    model = TimePeriodModel(id=999, name="custom")
    
    assert model.id == 999
    assert model.name == "custom"
    
    expected = "<TimePeriodModel(id=999, name='custom')"
    assert repr(model) == expected