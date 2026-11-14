"""
Chat API — streaming (SSE) and standard chat with Gemini + MongoDB logging.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.mongo import get_mongo_db
from app.models.pg_models import User
from app.schemas.schemas import ChatRequest, ChatResponse, MessageLogCreate
from app.services.gemini_service import stream_chat, complete_chat
from app.services.message_service import save_message
from app.services.conversation_service import create_conversation
from app.schemas.schemas import ConversationCreate
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/stream", summary="Streaming chat response (SSE)")
async def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a Server-Sent Events (SSE) stream.
    Frontend reads it with:
      const source = new EventSource('/api/chat/stream', { ... });
      source.onmessage = (e) => appendToken(e.data);
    """
    model = payload.model or settings.GEMINI_DEFAULT_MODEL
    conv_id = payload.conversation_id or str(uuid.uuid4())
    mongo_db = get_mongo_db()

    # Save user message to MongoDB
    await save_message(
        mongo_db,
        MessageLogCreate(
            conversation_id=conv_id,
            user_id=current_user.id,
            role="user",
            content=payload.message,
            model=model,
        ),
    )

    async def event_generator():
        full_reply = []
        try:
            async for chunk in stream_chat(payload.message, payload.history or [], model):
                full_reply.append(chunk)
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
            return

        # Save assistant reply to MongoDB
        reply_text = "".join(full_reply)
        await save_message(
            mongo_db,
            MessageLogCreate(
                conversation_id=conv_id,
                user_id=current_user.id,
                role="assistant",
                content=reply_text,
                model=model,
            ),
        )
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Conversation-Id": conv_id,
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/send", response_model=ChatResponse, summary="Non-streaming chat response")
async def chat_send(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Standard JSON response (no streaming)."""
    model = payload.model or settings.GEMINI_DEFAULT_MODEL
    conv_id = payload.conversation_id or str(uuid.uuid4())
    mongo_db = get_mongo_db()

    # Save user message
    await save_message(
        mongo_db,
        MessageLogCreate(
            conversation_id=conv_id,
            user_id=current_user.id,
            role="user",
            content=payload.message,
            model=model,
        ),
    )

    reply, tokens = await complete_chat(payload.message, payload.history or [], model)

    # Save assistant reply
    await save_message(
        mongo_db,
        MessageLogCreate(
            conversation_id=conv_id,
            user_id=current_user.id,
            role="assistant",
            content=reply,
            model=model,
            tokens=tokens,
        ),
    )

    return ChatResponse(conversation_id=conv_id, reply=reply, model=model, tokens_used=tokens)
