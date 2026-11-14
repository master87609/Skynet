"""
Conversations API — CRUD + message history retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.mongo import get_mongo_db
from app.models.pg_models import User
from app.schemas.schemas import (
    ConversationCreate,
    ConversationOut,
    ConversationUpdate,
)
from app.services.conversation_service import (
    create_conversation,
    list_conversations,
    get_conversation,
    update_conversation,
    delete_conversation,
)
from app.services.message_service import get_messages, delete_messages_for_conversation
from app.core.config import settings

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("/", response_model=list[ConversationOut])
async def list_convs(
    archived: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_conversations(db, current_user.id, include_archived=archived)


@router.post("/", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conv(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_conversation(db, current_user.id, payload, settings.GEMINI_DEFAULT_MODEL)


@router.get("/{conv_id}", response_model=ConversationOut)
async def get_conv(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation(db, conv_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.patch("/{conv_id}", response_model=ConversationOut)
async def patch_conv(
    conv_id: str,
    payload: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await update_conversation(db, conv_id, current_user.id, payload)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conv(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mongo_db = get_mongo_db()
    deleted = await delete_conversation(db, conv_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await delete_messages_for_conversation(mongo_db, conv_id)


@router.get("/{conv_id}/messages")
async def get_conv_messages(
    conv_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns full message history for a conversation from MongoDB."""
    conv = await get_conversation(db, conv_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    mongo_db = get_mongo_db()
    messages = await get_messages(mongo_db, conv_id, limit=limit)
    return {"conversation_id": conv_id, "messages": messages, "count": len(messages)}
