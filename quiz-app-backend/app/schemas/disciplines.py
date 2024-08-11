# filename: app/schemas/disciplines.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DisciplineBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the discipline")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Discipline name cannot be empty or whitespace')
        return v

class DisciplineCreateSchema(DisciplineBaseSchema):
    domain_ids: List[int] = Field(..., min_items=1, description="List of domain IDs associated with this discipline")
    subject_ids: Optional[List[int]] = Field(None, description="List of subject IDs associated with this discipline")

class DisciplineUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the discipline")
    domain_ids: Optional[List[int]] = Field(None, min_items=1, description="List of domain IDs associated with this discipline")
    subject_ids: Optional[List[int]] = Field(None, description="List of subject IDs associated with this discipline")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Discipline name cannot be empty or whitespace')
        return v

class DisciplineSchema(DisciplineBaseSchema):
    id: int
    domains: Optional[List[dict]] = Field(None, description="List of domains associated with this discipline")
    subjects: Optional[List[dict]] = Field(None, description="List of subjects associated with this discipline")

    @field_validator('domains', 'subjects', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True
