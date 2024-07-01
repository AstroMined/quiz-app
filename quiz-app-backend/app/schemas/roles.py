#filename: /app/schemas/roles.py

from typing import List
from pydantic import BaseModel


class RoleBaseSchema(BaseModel):
    name: str
    description: str

class RoleCreateSchema(RoleBaseSchema):
    permissions: List[str]

class RoleUpdateSchema(RoleBaseSchema):
    permissions: List[str]

class RoleSchema(RoleBaseSchema):
    id: int
    permissions: List[str]

    class Config:
        from_attributes = True
