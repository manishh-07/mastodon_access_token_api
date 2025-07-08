import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


# Mastodon base instance URL (e.g. http://localhost:3000 or https://social.example.com)
MASTODON_INSTANCE = os.getenv("MASTODON_INSTANCE", "http://localhost:3000")

# Client credentials (must be pre-registered manually once)
CLIENT_NAME = os.getenv("CLIENT_NAME", "MyFastAPIApp")
SCOPES = os.getenv("SCOPES", "read write follow")
MASTODON_CLIENT_ID = os.getenv("MASTODON_CLIENT_ID")
MASTODON_CLIENT_SECRET = os.getenv("MASTODON_CLIENT_SECRET")


# Docker container name for mastodon_web service
MASTODON_DOCKER = os.getenv("MASTODON_DOCKER", "mastodon_web_1")
    