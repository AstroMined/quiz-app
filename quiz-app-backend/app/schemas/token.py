# filename: app/schemas/token.py

from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
