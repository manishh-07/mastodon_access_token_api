
# 🚀 Mastodon Token Service (FastAPI)

This service creates or logs in Mastodon users, sets passwords (inside Dockerized Mastodon), and returns an access token using the `password` grant.

---

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

## 🔧 Prerequisites

- Mastodon installed inside Docker at `/opt/mastodon`
- This FastAPI service running separately (e.g., `/home/cepl/Desktop/mastodon_token_service/`)
- Mastodon web container name: `mastodon_web_1`
- A pre-registered OAuth app in Mastodon using:
  ```bash
  docker exec -it mastodon_web_1 bash -c "RAILS_ENV=production bin/tootctl apps create 'MyFastAPIApp' --redirect-uri urn:ietf:wg:oauth:2.0:oob --scopes 'read write follow'"
  ```


---

## ✅ Main API Usage

### ➤ `POST /generate-token`

Creates Mastodon account if not exists, sets password, returns token.

**Request JSON:**
```json
{
  "email": "giwison160@axcradio.com",
  "password": "mani1234"
}
```

**cURL:**
```bash
curl -X POST http://127.0.0.1:8000/generate-token \
  -H "Content-Type: application/json" \
  -d '{"email": "giwison160@axcradio.com", "password": "mani1234"}'
```

**Response JSON:**
```json
{
  "email": "giwison160@axcradio.com",
  "username": "giwison160",
  "access_token": "...",
  "token_type": "Bearer",
  "scope": "read write follow",
  "created_at": 1751000000
}
```

---

## 🧪 Manual OAuth Token Testing

If needed, use the same logic manually against Mastodon:

```bash
curl -X POST http://localhost:3000/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=-------------" \
  -d "client_secret=---------------" \
  -d "username=giwison160@axcradio.com" \
  -d "password=mani1234" \
  -d "scope=read write follow"
```

---

## 💡 Notes

- Mastodon username = sanitized email before `@` (e.g., `"giwison160@axcradio.com"` → `giwison160`)
- Password must be at least **8 characters**
- `redirect_uri` must match `urn:ietf:wg:oauth:2.0:oob` (important!)
- `/generate-token` works on both new & existing users
- All token requests rely on fixed `client_id` and `client_secret` from `.env`

---

## 🧼 Debug/Check Commands

Check if Mastodon user exists:

```bash
docker exec -it mastodon_web_1 bash -c "RAILS_ENV=production bin/rails c"
```

Then in Rails console:
```ruby
Account.exists?(username: "giwison160")
User.find_by(email: "giwison160@axcradio.com")
```

---

## 📅 Generated On

2025-07-07 05:57:59 UTC

---