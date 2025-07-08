import subprocess
import requests
import re
import os
from app.config import (
    MASTODON_INSTANCE, CLIENT_NAME, SCOPES,
    MASTODON_DOCKER, MASTODON_CLIENT_ID, MASTODON_CLIENT_SECRET
)

def run_in_container(command: list):
    """
    Run a shell command inside the Mastodon Docker container.
    """
    full_command = f"docker exec {MASTODON_DOCKER} bash -c \"{' '.join(command)}\""
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
    print("🔧 CMD:", full_command)
    print("🔧 STDOUT:", result.stdout.strip())
    print("🔧 STDERR:", result.stderr.strip())
    print("🔧 RETURN CODE:", result.returncode)
    return result

def sanitize_username_from_email(email: str) -> str:
    """
    Converts an email address to a Mastodon-safe username.
    Example: "user@example.com" → "user"
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', email.split("@")[0])

def create_mastodon_account(username: str, email: str, password: str):
    """
    Creates a Mastodon account (if it does not exist) and sets its password.
    """
    if len(password) < 8:
        raise Exception("Password must be at least 8 characters long.")

    print(f"🔧 Creating Mastodon user '{username}'...")

    create_cmd = [f"RAILS_ENV=production bin/tootctl accounts create {username} --email={email} --confirmed"]
    create_result = run_in_container(create_cmd)

    if "has already been taken" in create_result.stderr:
        print(f"Mastodon user '{username}' already exists. Skipping creation.")
    elif create_result.returncode != 0:
        raise Exception(f"Error creating user:\n{create_result.stderr or create_result.stdout}")

    # Set the password using a Rails runner command
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
        raise Exception(f"Failed to set password:\n{password_result.stderr or password_result.stdout}")

    print("Mastodon account ready.")

def get_token_for_user(email: str, password: str):
    """
    Requests an access token using the 'password' grant.
    Note: The Doorkeeper config expects the 'username' parameter to be the full email.
    """
    if not MASTODON_CLIENT_ID or not MASTODON_CLIENT_SECRET:
        raise Exception("Missing MASTODON_CLIENT_ID or MASTODON_CLIENT_SECRET.")

    token_url = f"{MASTODON_INSTANCE}/oauth/token"
    response = requests.post(token_url, data={
        "grant_type": "password",
        "client_id": MASTODON_CLIENT_ID,
        "client_secret": MASTODON_CLIENT_SECRET,
        "username": email,  # Pass the full email, not the sanitized username
        "password": password,
        "scope": SCOPES
    })

    if not response.ok:
        raise Exception(f"Token request failed: {response.status_code} {response.text}")
    return response.json()

def generate_access_token(email: str, password: str):
    """
    Full flow: sanitizes username for local use, creates the account, and gets an access token.
    """
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

def change_password(email: str, old_password: str, new_password: str):
    """
    For logged-in users: verifies the old password, then changes to the new password.
    """
    if len(new_password) < 8:
        raise Exception("Password must be at least 8 characters.")
    # Validate the old password
    get_token_for_user(email, old_password)
    username = sanitize_username_from_email(email)
    ruby = (
        f"user = Account.find_by(username: '{username}').user;"
        f"user.password = '{new_password}';"
        f"user.password_confirmation = '{new_password}';"
        f"user.save!"
    )
    safe_ruby = ruby.replace("'", "'\\''")
    cmd = [f"RAILS_ENV=production bin/rails runner '{safe_ruby}'"]
    result = run_in_container(cmd)
    if result.returncode != 0:
        raise Exception(f"Failed to change password:\n{result.stderr or result.stdout}")
    print("Password changed.")

def forgot_password(email: str, new_password: str):
    if len(new_password) < 8:
        raise Exception("Password must be at least 8 characters.")
    username = sanitize_username_from_email(email)

    ruby_check = f"puts User.find_by(email: '{email}').present?"
    safe_check = ruby_check.replace("'", "'\\''")
    check_cmd = [f"RAILS_ENV=production bin/rails runner '{safe_check}'"]
    result = run_in_container(check_cmd)

    if "true" not in result.stdout:
        raise Exception("Email not found.")

    ruby = (
        f"user = Account.find_by(username: '{username}').user;"
        f"user.skip_confirmation! if user.respond_to?(:skip_confirmation!);"
        f"user.password = '{new_password}';"
        f"user.password_confirmation = '{new_password}';"
        f"user.save!"
    )
    safe_ruby = ruby.replace("'", "'\\''")
    cmd = [f"RAILS_ENV=production bin/rails runner '{safe_ruby}'"]
    result = run_in_container(cmd)

    if result.returncode != 0:
        raise Exception("Failed to reset password.")
    print("Password reset.")
