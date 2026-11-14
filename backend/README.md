# SKYNET AI — Backend

A production-ready **FastAPI** backend for the SKYNET AI platform, featuring:

- 🤖 **AI Chat** (Google Gemini 2.0 Flash — streaming SSE + standard JSON)
- 🔐 **Authentication** (Google OAuth2 + Email/Host Trial via JWT)
- 💬 **Conversation History** (PostgreSQL metadata + MongoDB message logs)
- 💳 **Billing & Subscriptions** (Free → Pro → Max/Ultra, INR pricing)

---

## 📁 Project Structure

```
skynet-backend/
├── app/
│   ├── api/
│   │   ├── auth.py           # POST /api/auth/google, /email, /refresh
│   │   ├── chat.py           # POST /api/chat/stream, /send
│   │   ├── conversations.py  # CRUD /api/conversations
│   │   ├── billing.py        # POST /api/billing/subscribe
│   │   ├── users.py          # GET/PATCH /api/users/me
│   │   └── deps.py           # JWT auth dependency
│   ├── core/
│   │   ├── config.py         # Settings from .env
│   │   ├── database.py       # PostgreSQL async engine
│   │   ├── mongo.py          # MongoDB Motor client
│   │   └── security.py       # JWT create/decode
│   ├── models/
│   │   └── pg_models.py      # SQLAlchemy ORM: User, Conversation, Subscription
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── services/
│   │   ├── auth_service.py      # Google token verify + user upsert
│   │   ├── gemini_service.py    # Gemini streaming + non-streaming
│   │   ├── conversation_service.py # PostgreSQL CRUD
│   │   └── message_service.py   # MongoDB message log CRUD
│   └── main.py               # FastAPI app + lifespan
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.12+
- PostgreSQL running locally (or remote URL)
- MongoDB running locally (or MongoDB Atlas URL)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Google OAuth2 Client ID ([Create here](https://console.cloud.google.com/apis/credentials))

### 2. Setup

```bash
cd skynet-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and fill in your API keys and DB URLs
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

**Docs available at:** http://localhost:8000/docs

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/google` | Login with Google ID token |
| `POST` | `/api/auth/email` | Login with email (host trial) |
| `POST` | `/api/auth/refresh` | Refresh JWT access token |
| `GET` | `/api/users/me` | Get logged-in user profile |
| `PATCH` | `/api/users/me` | Update name / avatar |
| `POST` | `/api/chat/stream` | Streaming SSE chat (Gemini) |
| `POST` | `/api/chat/send` | Standard JSON chat response |
| `GET` | `/api/conversations` | List all conversations |
| `POST` | `/api/conversations` | Create new conversation |
| `GET` | `/api/conversations/{id}` | Get conversation metadata |
| `PATCH` | `/api/conversations/{id}` | Rename or archive |
| `DELETE` | `/api/conversations/{id}` | Delete conversation + messages |
| `GET` | `/api/conversations/{id}/messages` | Full message history (MongoDB) |
| `POST` | `/api/billing/subscribe` | Activate Pro/Max plan |
| `GET` | `/api/billing/subscription` | Get current subscription |
| `DELETE`| `/api/billing/cancel` | Cancel subscription |

---

## 🌐 Frontend Integration

### Chat streaming (from `index.html`):
```javascript
const response = await fetch('http://localhost:8000/api/chat/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  },
  body: JSON.stringify({
    message: "Hello SKYNET!",
    conversation_id: activeConvId,
    history: chatHistory,
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const text = decoder.decode(value);
  // Parse SSE lines: "data: TOKEN\n\n"
  text.split('\n').forEach(line => {
    if (line.startsWith('data: ')) {
      const token = line.slice(6);
      if (token !== '[DONE]') appendToLastMessage(token);
    }
  });
}
```

---

## 🗄️ Database Design

### PostgreSQL (`skynet_db`)
- **users** — email, name, avatar, google_id, plan, is_host
- **conversations** — user_id, title, model, is_archived
- **subscriptions** — user_id, plan, billing_cycle, payment_method, amount_inr

### MongoDB (`skynet_logs`)
- **messages** — conversation_id, user_id, role, content, model, tokens, created_at

> Tables are auto-created on first startup via SQLAlchemy.
