import subprocess
import requests
import re
import os
from app.config import (
    MASTODON_INSTANCE, CLIENT_NAME, SCOPES,
    MASTODON_DOCKER, MASTODON_CLIENT_ID, MASTODON_CLIENT_SECRET
)

def run_in_container(command: list):
    full_command = f"docker exec {MASTODON_DOCKER} bash -c \"{' '.join(command)}\""
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)

    print("🔧 CMD:", full_command)
    print("🔧 STDOUT:", result.stdout.strip())
    print("🔧 STDERR:", result.stderr.strip())
    print("🔧 RETURN CODE:", result.returncode)
    return result

def sanitize_username_from_email(email: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', email.split("@")[0])

def create_mastodon_account(username: str, email: str, password: str):
    if len(password) < 8:
        raise Exception("❌ Password must be at least 8 characters long.")

    print(f"🔧 Creating Mastodon user '{username}'...")

    create_cmd = [
        f"RAILS_ENV=production bin/tootctl accounts create {username} --email={email} --confirmed"
    ]
    create_result = run_in_container(create_cmd)

    if "has already been taken" in create_result.stderr:
        print(f"⚠️ Mastodon user '{username}' already exists. Skipping creation.")
    elif create_result.returncode != 0:
        raise Exception(f"❌ Error creating user:\n{create_result.stderr or create_result.stdout}")

    ruby = (
        f"user = Account.find_by(username: '{username}').user;"
        f"user.password = '{password}';"
        f"user.password_confirmation = '{password}';"
        f"user.save!"
    )
    safe_ruby = ruby.replace("'", "'\\''")

    rails_cmd = [f"RAILS_ENV=production bin/rails runner '{safe_ruby}'"]
    password_result = run_in_container(rails_cmd)

    if password_result.returncode != 0:
        raise Exception(f"❌ Failed to set password:\n{password_result.stderr or password_result.stdout}")

    print("✅ Mastodon account ready.")

def get_token_for_user(email: str, password: str):
    if not MASTODON_CLIENT_ID or not MASTODON_CLIENT_SECRET:
        raise Exception("❌ Missing MASTODON_CLIENT_ID or MASTODON_CLIENT_SECRET.")

    token_url = f"{MASTODON_INSTANCE}/oauth/token"
    response = requests.post(token_url, data={
        "grant_type": "password",
        "client_id": MASTODON_CLIENT_ID,
        "client_secret": MASTODON_CLIENT_SECRET,
        "username": email,  # email as username
        "password": password,
        "scope": SCOPES
    })

    if not response.ok:
        raise Exception(f"❌ Token request failed: {response.status_code} {response.text}")

    return response.json()

def generate_access_token(email: str, password: str):
    username = sanitize_username_from_email(email)
    create_mastodon_account(username, email, password)
    token_data = get_token_for_user(email, password)

    return {
        "email": email,
        "username": username,
        "access_token": token_data.get("access_token"),
        "token_type": token_data.get("token_type"),
        "scope": token_data.get("scope"),
        "created_at": token_data.get("created_at")
    }
