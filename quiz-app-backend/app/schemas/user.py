# filename: app/schemas/user.py
from pydantic import BaseModel, validator
class UserCreate(BaseModel):
    username: str
    password: str

    @validator('password')
    def password_validation(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Add more rules as necessary
        return v
class UserLogin(BaseModel):
    username: str
    password: str
