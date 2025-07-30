import requests
import os
from app.config import MASTODON_INSTANCE, CLIENT_NAME, SCOPES

def register_oauth_app_once():
    if os.getenv("MASTODON_CLIENT_ID") and os.getenv("MASTODON_CLIENT_SECRET"):
        print("✅ OAuth App already registered.")
        return

    print("⚙️ Registering new Mastodon OAuth app...")

    register_url = f"{MASTODON_INSTANCE}/api/v1/apps"
    response = requests.post(register_url, data={
        "client_name": CLIENT_NAME,
        "redirect_uris": "https://99138a0ecaf4.ngrok-free.app/callback",  # <-- ✅ use ngrok FastAPI URL
        "scopes": SCOPES,
        "website": "http://localhost"
})

    if response.status_code != 200:
        raise Exception(f"OAuth registration failed: {response.status_code} {response.text}")

    data = response.json()
    print("✅ OAuth App Registered")
    print("CLIENT ID:", data["client_id"])
    print("CLIENT SECRET:", data["client_secret"])

    # Optional: Auto-write to env (not recommended in Docker)
    with open(".env", "a") as f:
        f.write(f"\nMASTODON_CLIENT_ID={data['client_id']}")
        f.write(f"\nMASTODON_CLIENT_SECRET={data['client_secret']}")

