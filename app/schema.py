from pydantic import BaseModel

class TokenRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    email: str
    username: str
    access_token: str
    token_type: str
    scope: str
    created_at: int

