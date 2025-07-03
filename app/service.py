import requests
from app.config import MASTODON_INSTANCE, CLIENT_NAME, SCOPES

_client_id = None
_client_secret = None

def register_app():
    global _client_id, _client_secret

    if _client_id and _client_secret:
        return _client_id, _client_secret

    url = f"{MASTODON_INSTANCE}/api/v1/apps"
    resp = requests.post(url, data={
        "client_name": CLIENT_NAME,
        "redirect_uris": "urn:ietf:wg:oauth:2.0:oob",
        "scopes": SCOPES,
        "website": "http://localhost"
    })
    resp.raise_for_status()
    data = resp.json()
    _client_id = data["client_id"]
    _client_secret = data["client_secret"]
    return _client_id, _client_secret

def generate_access_token(username: str, password: str):
    client_id, client_secret = register_app()

    token_url = f"{MASTODON_INSTANCE}/oauth/token"
    response = requests.post(token_url, data={
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password,
        "scope": SCOPES
    })

    if not response.ok:
        raise Exception(f"Token request failed: {response.status_code} {response.text}")
    return response.json()
