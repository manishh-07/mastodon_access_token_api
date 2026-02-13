
# 🚀 Mastodon's Account Creation, Access Token & Password Management via FastAPI (Debugging Branch)

This project provides **three fully automated FastAPI endpoints** to interact with a self-hosted Mastodon instance running in Docker.

## 📁 Project Structure

```
/mastodon_token_service/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration from .env
│   ├── service.py           # Mastodon logic (create account, get token)
│   └── schema.py            # Pydantic schemas
├── .env                     # Environment secrets
└── README.txt               # This file
```


---

## 📦 Endpoints Summary

| Endpoint            | Description                            | Auth Required |
|---------------------|----------------------------------------|---------------|
| `/generate-token`   | Auto-creates a Mastodon user (if needed), sets password, and returns an access token using the password grant | ❌ No |
| `/change-password`  | Changes the password of a Mastodon user after validating old password | ✅ Yes |
| `/forgot-password`  | Resets a user's password without login (unauthenticated flow) | ❌ No |

---

## ⚙️ Internals – What Happens Under the Hood?

### 1. 🔑 `/generate-token`

- Extracts `username` from email (sanitizing special characters)
- Runs inside Mastodon container:
  - `bin/tootctl accounts create ...`
  - If already exists: skips
- Then sets password:
  ```ruby
  user = Account.find_by(username: '<username>').user
  user.password = '<password>'
  user.save!
  ```
- Then uses `client_id` and `client_secret` with:
  ```http
  POST /oauth/token
  grant_type=password
  ```

---

### 2. 🔁 `/change-password`

- Verifies identity using:
  ```http
  POST /oauth/token
  grant_type=password
  ```
- Then inside container:
  ```ruby
  user = Account.find_by(username: '<username>').user
  user.password = '<new_password>'
  user.save!
  ```

---

### 3. 🧠 `/forgot-password`

- Verifies user existence via:
  ```ruby
  puts User.find_by(email: '<email>').present?
  ```
- Resets password directly using:
  ```ruby
  user = Account.find_by(username: '<username>').user
  user.skip_confirmation!
  user.password = '<new_password>'
  user.save!
  ```

---

## 🔐 Mastodon Setup Notes (One-Time)

1. Enter Mastodon container:
```bash
docker exec -it mastodon_web_1 bash
```

2. Generate credentials:
```bash
RAILS_ENV=production bin/tootctl applications create MyFastAPIApp \
  --redirect-uri=urn:ietf:wg:oauth:2.0:oob \
  --scopes="read write follow"
```

3. Save the `client_id` and `client_secret` in your `.env`.

---

## 📁 .env Example (Safe for Production)

```env
# For Running Ngrok server 

# ngrok start --all --config ~/.ngrok2/ngrok.yml

CLIENT_NAME=MyNgrokApp
SCOPES=read write follow
MASTODON_DOCKER=mastodon_web_1
MASTODON_INSTANCE=https://0b44d52cd.ngrok-free.app
MASTODON_CLIENT_ID=GpQ6Pzm9Tlfkz2_RP1zQLWnYxiQpoqRCM
MASTODON_CLIENT_SECRET=0VKES7HvIZRSL-ttaY7LboHqwgnNW_gS228oaqVM
```

---

## 🐳 Docker Compatibility

Make sure both **FastAPI container** and **Mastodon containers** are on the **same network**:
```yaml
networks:
  mastodon:
    driver: bridge
```

---

## 🧪 Testing Reference (Postman / Curl)

### Check endpoints carefully
### ✅ Generate Token
```bash
curl -X POST http://127.0.0.1:8000/generate-token \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@tempmail.com", "password": "mani1234"}'
```

### 🔁 Change Password
```bash
curl -X POST http://127.0.0.1:8000/change-password \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@tempmail.com", "old_password": "mani1234", "new_password": "newsecure123"}'
```

### 🧠 Forgot Password
```bash
curl -X POST http://127.0.0.1:8000/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@tempmail.com", "new_password": "root1234"}'
```
---

## ⚠️ WARNING: Invalid Client / Token Request Failure

### If you see this error:
```bash
{    "error": "invalid_client",    "error_description": "Client authentication failed due to unknown client, no client authentication included, or unsupported authentication method."  }
```

### 🔍 Cause:
```bash
*   This happens when .env is updated but your FastAPI server is still using old environment values.
```

### ✅ Solution:
```bash

1.  Update your.env file with new MASTODON\_CLIENT\_ID and MASTODON\_CLIENT\_SECRET.
```

```bash
2.  Then fully restart your FastAPI server not just --reload:
```

 ```bash
   3. Kill existing  CTRL+C  # Restart the server  uvicorn app.main:app --reload   `
```

This ensures environment values are reloaded cleanly.

---

uvicorn app.main:app --reload

```

## 📅 Last Updated

2025-07-08 05:58:08

---
