# filename: app/schemas/subjects.py

from pydantic import BaseModel, validator

class SubjectBaseSchema(BaseModel):
    name: str

class SubjectCreateSchema(SubjectBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Subject name cannot exceed 100 characters')
        return name

class SubjectSchema(SubjectBaseSchema):
    id: int

    class Config:
        from_attributes = True
