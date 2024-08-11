# filename: app/schemas/time_period.py

from pydantic import BaseModel, Field, field_validator, model_validator


class TimePeriodSchema(BaseModel):
    id: int = Field(..., gt=0, description="ID of the time period")
    name: str = Field(..., min_length=1, max_length=20, description="Name of the time period")

    @field_validator('name')
    @classmethod
    def name_must_be_valid(cls, v):
        valid_names = {"daily", "weekly", "monthly", "yearly"}
        if v not in valid_names:
            raise ValueError(f"Name must be one of: daily, weekly, monthly, yearly")
        return v

    @model_validator(mode='after')
    def check_id_name_combination(self):
        id_name_map = {1: "daily", 7: "weekly", 30: "monthly", 365: "yearly"}
        if self.name != id_name_map.get(self.id):
            raise ValueError(f"Invalid combination of id and name. For id {self.id}, name should be {id_name_map.get(self.id)}")
        return self

    class Config:
        from_attributes = True
