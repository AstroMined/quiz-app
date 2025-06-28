# filename: backend/tests/unit/models/test_enums_and_config.py

import pytest
from pydantic import ValidationError

from backend.app.core.config import (
    DifficultyLevel, 
    DifficultyLevelModel, 
    TimePeriod, 
    TimePeriodModel
)


def test_difficulty_level_enum_values():
    """Test DifficultyLevel enum has correct values."""
    assert DifficultyLevel.BEGINNER == "Beginner"
    assert DifficultyLevel.EASY == "Easy"
    assert DifficultyLevel.MEDIUM == "Medium"
    assert DifficultyLevel.HARD == "Hard"
    assert DifficultyLevel.EXPERT == "Expert"


def test_difficulty_level_enum_str_representation():
    """Test DifficultyLevel enum string representation."""
    assert str(DifficultyLevel.BEGINNER) == "DifficultyLevel.BEGINNER"
    assert str(DifficultyLevel.EASY) == "DifficultyLevel.EASY"
    assert str(DifficultyLevel.MEDIUM) == "DifficultyLevel.MEDIUM"
    assert str(DifficultyLevel.HARD) == "DifficultyLevel.HARD"
    assert str(DifficultyLevel.EXPERT) == "DifficultyLevel.EXPERT"


def test_time_period_enum_values():
    """Test TimePeriod enum has correct integer values."""
    assert TimePeriod.DAILY == 1
    assert TimePeriod.WEEKLY == 7
    assert TimePeriod.MONTHLY == 30
    assert TimePeriod.YEARLY == 365


def test_time_period_enum_value_property():
    """Test TimePeriod enum value property."""
    assert TimePeriod.DAILY.value == 1
    assert TimePeriod.WEEKLY.value == 7
    assert TimePeriod.MONTHLY.value == 30
    assert TimePeriod.YEARLY.value == 365


def test_time_period_get_name_class_method():
    """Test TimePeriod.get_name() class method."""
    assert TimePeriod.get_name(1) == "daily"
    assert TimePeriod.get_name(7) == "weekly"
    assert TimePeriod.get_name(30) == "monthly"
    assert TimePeriod.get_name(365) == "yearly"


def test_time_period_get_name_with_enum_instance():
    """Test TimePeriod.get_name() with enum instances."""
    assert TimePeriod.get_name(TimePeriod.DAILY.value) == "daily"
    assert TimePeriod.get_name(TimePeriod.WEEKLY.value) == "weekly"
    assert TimePeriod.get_name(TimePeriod.MONTHLY.value) == "monthly"
    assert TimePeriod.get_name(TimePeriod.YEARLY.value) == "yearly"


def test_difficulty_level_pydantic_model_valid():
    """Test DifficultyLevelModel with valid enum values."""
    model = DifficultyLevelModel(difficulty=DifficultyLevel.EASY)
    assert model.difficulty == DifficultyLevel.EASY
    assert model.difficulty.value == "Easy"


def test_difficulty_level_pydantic_model_all_values():
    """Test DifficultyLevelModel with all enum values."""
    for level in DifficultyLevel:
        model = DifficultyLevelModel(difficulty=level)
        assert model.difficulty == level


def test_time_period_pydantic_model_valid():
    """Test TimePeriodModel (Pydantic) with valid enum values.""" 
    # Note: This tests the Pydantic TimePeriodModel from config.py, not the SQLAlchemy one
    from backend.app.core.config import TimePeriodModel as PydanticTimePeriodModel
    
    model = PydanticTimePeriodModel(time_period=TimePeriod.WEEKLY)
    assert model.time_period == TimePeriod.WEEKLY
    assert model.time_period.value == 7


def test_time_period_pydantic_model_all_values():
    """Test TimePeriodModel (Pydantic) with all enum values."""
    from backend.app.core.config import TimePeriodModel as PydanticTimePeriodModel
    
    for period in TimePeriod:
        model = PydanticTimePeriodModel(time_period=period)
        assert model.time_period == period


def test_time_period_get_name_invalid_value():
    """Test TimePeriod.get_name() with invalid value raises error."""
    with pytest.raises(ValueError):
        TimePeriod.get_name(999)


def test_difficulty_level_enum_comparison():
    """Test DifficultyLevel enum comparison and identity."""
    easy1 = DifficultyLevel.EASY
    easy2 = DifficultyLevel.EASY
    medium = DifficultyLevel.MEDIUM
    
    assert easy1 == easy2
    assert easy1 is easy2
    assert easy1 != medium
    assert easy1 is not medium