# SKYNET AI — Full-Stack Platform

A complete AI assistant platform featuring a desktop/web frontend with kinetic typography, animations, and multi-conversation management, paired with a high-performance **FastAPI** backend supporting **Google Gemini 2.0 streaming (SSE)**, **PostgreSQL** relational data, **MongoDB** message logs, **Google OAuth2** authentication, and tier subscriptions.

---

## 🏛️ System Architecture

```
Skynet/
├── index.html                  # Production Frontend Application (SPA)
├── backend/                    # FastAPI Backend Service
│   ├── app/
│   │   ├── api/                # API Endpoints
│   │   │   ├── auth.py         # Google OAuth2 + Email (Host Trial) JWT login
│   │   │   ├── chat.py         # Streaming (SSE) & standard chat with Gemini
│   │   │   ├── conversations.py# Conversation CRUD & message history
│   │   │   ├── billing.py      # Plan subscription & upgrade/downgrade
│   │   │   ├── users.py        # Profile view and update
│   │   │   └── deps.py         # JWT authentication dependency
│   │   ├── core/               # App configuration & DB connections
│   │   │   ├── config.py       # Pydantic environment settings (.env)
│   │   │   ├── database.py     # PostgreSQL AsyncSession (SQLAlchemy)
│   │   │   ├── mongo.py        # MongoDB Async Motor client
│   │   │   └── security.py     # JWT token creation & verification
│   │   ├── models/             # Database ORM Models
│   │   │   └── pg_models.py    # Users, Conversations, Subscriptions
│   │   ├── schemas/            # Pydantic Schemas (validation)
│   │   │   └── schemas.py      # Request/response contracts
│   │   ├── services/           # Business logic layer
│   │   │   ├── auth_service.py # Google token validation + user upsert
│   │   │   ├── gemini_service.py # Gemini 2.0 streaming & completion
│   │   │   ├── conversation_service.py # PostgreSQL conversation CRUD
│   │   │   └── message_service.py # MongoDB high-throughput chat storage
│   │   └── main.py             # FastAPI entry point & CORS configuration
│   ├── requirements.txt        # Python backend dependencies
│   ├── .env.example            # Environment variables template
│   └── README.md               # Backend-specific documentation
├── README.md                   # Project overview & quickstart
└── .gitignore
```

---

## 🚀 Quickstart

### 1. Start the Backend (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
# Fill in your GEMINI_API_KEY, POSTGRES_URL, MONGO_URL, etc.

# Run server
uvicorn app.main:app --reload --port 8000
```

* **Interactive API Docs (Swagger):** `http://localhost:8000/docs`
* **Alternative API Docs (ReDoc):** `http://localhost:8000/redoc`

---

### 2. Start the Frontend

From the repository root:

```bash
# Using Python built-in server
python -m http.server 8080

# Or using npx serve
npx serve -l 8080
```

Open `http://localhost:8080` in your web browser.

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/google` | Login/signup via Google OAuth2 ID Token |
| `POST` | `/api/auth/email` | Instant Email login (Host Trial phase) |
| `POST` | `/api/auth/refresh` | Refresh expired JWT access token |
| `GET` | `/api/users/me` | Fetch active user profile and subscription |
| `PATCH`| `/api/users/me` | Update display name or avatar |
| `POST` | `/api/chat/stream` | Server-Sent Events (SSE) streaming chat via Gemini |
| `POST` | `/api/chat/send` | Synchronous JSON chat response |
| `GET` | `/api/conversations` | List user conversation threads |
| `POST` | `/api/conversations` | Create new conversation |
| `GET` | `/api/conversations/{id}/messages` | Retrieve conversation message history |
| `DELETE`| `/api/conversations/{id}` | Delete conversation and related messages |
| `POST` | `/api/billing/subscribe` | Activate or upgrade subscription (Pro/Max/Ultra) |
| `GET` | `/api/billing/subscription` | Get current active subscription details |

---

## 🗄️ Database Strategy

* **PostgreSQL (Structured Relational Data):**
  * `users`: Profiles, OAuth IDs, active plans, host privileges.
  * `conversations`: Conversation titles, creation dates, assigned model.
  * `subscriptions`: Plan tier, payment method, validity periods.
* **MongoDB (High-Velocity Document Storage):**
  * `messages`: Message payloads, roles (`user`, `assistant`), token counts, and timestamps.
