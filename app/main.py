from fastapi import FastAPI, HTTPException
from app.schema import TokenRequest, TokenResponse
from app.service import generate_access_token

app = FastAPI()

@app.post("/generate-token", response_model=TokenResponse)
def get_token(data: TokenRequest):
    try:
        token_data = generate_access_token(data.username, data.password)
        return token_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
