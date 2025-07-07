from fastapi import FastAPI, HTTPException
from app.schema import TokenRequest, TokenResponse
from app.service import generate_access_token

app = FastAPI()

@app.post("/generate-token", response_model=TokenResponse)
def generate_token(payload: TokenRequest):
    try:
        return generate_access_token(payload.email, payload.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
