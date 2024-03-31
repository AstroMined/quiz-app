from pydantic import BaseModel, Field

class LoginForm(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
