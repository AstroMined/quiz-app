# filename: backend/app/schemas/domains.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DomainBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the domain")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Domain name cannot be empty or whitespace')
        return v

class DomainCreateSchema(DomainBaseSchema):
    discipline_ids: Optional[List[int]] = Field(None, description="List of discipline IDs associated with this domain")

class DomainUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the domain")
    discipline_ids: Optional[List[int]] = Field(None, description="List of discipline IDs associated with this domain")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Domain name cannot be empty or whitespace')
        return v

class DomainSchema(DomainBaseSchema):
    id: Optional[int] = Field(None, description="ID of the domain")
    disciplines: Optional[List[dict]] = Field(None, description="List of disciplines associated with this domain")

    @field_validator('disciplines', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True
