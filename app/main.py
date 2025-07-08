from fastapi import FastAPI, HTTPException
from app.schema import (
    TokenRequest, TokenResponse,
    PasswordChangeRequest, ForgotPasswordRequest
)
from app.service import (
    generate_access_token, change_password, forgot_password
)
from app.utils import register_oauth_app_once  # 👈 NEW FUNCTION

app = FastAPI()


@app.on_event("startup")
def startup_event():
    try:
        register_oauth_app_once()  # ✅ Register the OAuth client only once
    except Exception as e:
        print("❌ Failed to register OAuth app:", e)


@app.post("/generate-token", response_model=TokenResponse)
def generate_token(payload: TokenRequest):
    try:
        return generate_access_token(payload.email, payload.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/change-password")
def change_password_route(data: PasswordChangeRequest):
    try:
        change_password(data.email, data.old_password, data.new_password)
        return {"detail": "✅ Password changed successfully."}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/forgot-password")
def forgot_password_route(data: ForgotPasswordRequest):
    try:
        forgot_password(data.email, data.new_password)
        return {"detail": "✅ Password reset successfully (via forgot-password)."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
