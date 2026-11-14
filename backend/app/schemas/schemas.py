"""
Pydantic Schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ── Auth ────────────────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    id_token: str  # Google ID token from frontend


class EmailAuthRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    is_host: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    plan: str
    is_host: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


# ── Chat ─────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    model: Optional[str] = None
    history: Optional[List[ChatMessage]] = []
    stream: bool = True


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    model: str
    tokens_used: Optional[int] = None


# ── Conversation ─────────────────────────────────────────────────

class ConversationOut(BaseModel):
    id: str
    title: str
    model: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    title: str = "New conversation"
    model: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None


# ── Billing ───────────────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    plan: str = Field(..., pattern="^(pro|max|ultra)$")
    billing_cycle: str = Field("monthly", pattern="^(monthly|yearly)$")
    payment_method: str = Field(..., pattern="^(upi|card|netbanking)$")


class SubscriptionOut(BaseModel):
    plan: str
    billing_cycle: str
    payment_method: Optional[str]
    amount_inr: int
    is_active: bool
    activated_at: datetime
    expires_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Message Log (MongoDB) ─────────────────────────────────────────

class MessageLogCreate(BaseModel):
    conversation_id: str
    user_id: str
    role: str
    content: str
    model: str
    tokens: Optional[int] = 0


class MessageLogOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    model: str
    tokens: int
    created_at: datetime
