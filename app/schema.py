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

class PasswordChangeRequest(BaseModel):
    email: str
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str