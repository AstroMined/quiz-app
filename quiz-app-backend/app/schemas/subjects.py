# filename: app/schemas/subjects.py

from pydantic import BaseModel

class SubjectBaseSchema(BaseModel):
    name: str

class SubjectCreateSchema(SubjectBaseSchema):
    pass

class SubjectSchema(SubjectBaseSchema):
    id: int

    class Config:
        from_attributes = True
