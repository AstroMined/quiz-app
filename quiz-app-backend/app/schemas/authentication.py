# filename: app/schemas/authentication.py

from pydantic import BaseModel, Field


class LoginFormSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
