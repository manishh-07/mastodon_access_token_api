import os
from dotenv import load_dotenv

load_dotenv()

MASTODON_INSTANCE = os.getenv("MASTODON_INSTANCE", "http://localhost:3000")
CLIENT_NAME = os.getenv("CLIENT_NAME", "MyFastAPIApp")
SCOPES = os.getenv("SCOPES", "read write follow")
