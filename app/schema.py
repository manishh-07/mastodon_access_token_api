from pydantic import BaseModel

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    scope: str
    created_at: int

