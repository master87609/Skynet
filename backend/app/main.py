"""
SKYNET AI Backend — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.mongo import close_mongo
from app.api import auth, chat, conversations, billing, users, agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ─────────────────────────────────────────
    print("🚀 SKYNET Backend starting up...")
    try:
        await init_db()         # Create PostgreSQL tables if database accessible
        print("✅ PostgreSQL tables ready")
    except Exception as e:
        print(f"⚠️ PostgreSQL connection deferred: {e}")
    print("✅ MongoDB connection lazy-initialized")
    print("✅ Multi-Agent Website Builder Team active")
    yield
    # ── Shutdown ─────────────────────────────────────────
    await close_mongo()
    print("💤 SKYNET Backend shut down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "SKYNET AI backend — Powers chat (Gemini), Multi-Agent Website Builder Studio, "
        "authentication (Google OAuth2 + Email), conversation history (PostgreSQL + MongoDB), "
        "and billing/subscription management."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────
app.include_router(auth.router,          prefix="/api")
app.include_router(chat.router,          prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(billing.router,       prefix="/api")
app.include_router(users.router,         prefix="/api")
app.include_router(agents.router,        prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
