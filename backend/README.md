# SKYNET AI — Backend

A production-ready **FastAPI** backend for the SKYNET AI platform, featuring:

- 🌐 **Multi-Agent Website Builder Team** (5 Collaborative Agents: Architect, Copywriter, Designer, Coder, QA)
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
│   │   ├── agents.py         # POST /api/agents/website/build, /refine, /download
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
│   │   ├── website_agent_team.py # 5-Agent Collaborative Website Studio
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

## 🤖 Integrated Website Builder Agent Team

The backend features an autonomous multi-agent swarm:
1. **Architect Agent:** Analyzes the prompt, determines category, design tokens, sitemap, and component hierarchy.
2. **Copywriter Agent:** Crafts engaging headlines, benefit bullets, value propositions, and call-to-actions.
3. **Designer Agent:** Selects the modern Tailwind color scheme, typography scales, glassmorphism, and responsive breakpoints.
4. **Coder Agent:** Synthesizes the architecture, copy, and layout into complete, standalone, production-ready HTML5 + Tailwind CSS + Vanilla JS.
5. **QA Reviewer Agent:** Audits mobile responsiveness, viewport configurations, and interactivity.

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agents/website/build` | SSE streaming endpoint running the 5 agents with live status updates and final HTML |
| `POST` | `/api/agents/website/refine`| Modifies specific sections based on user feedback |
| `POST` | `/api/agents/website/download`| Downloads the standalone `index.html` |

---

## ⚡ Quick Start

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and fill in your API keys and DB URLs

# Run the Server
uvicorn app.main:app --reload --port 8000
```

**Docs available at:** http://localhost:8000/docs
