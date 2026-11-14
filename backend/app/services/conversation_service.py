"""
Conversation Service — CRUD in PostgreSQL.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.pg_models import Conversation
from app.schemas.schemas import ConversationCreate, ConversationUpdate


async def create_conversation(
    db: AsyncSession, user_id: str, payload: ConversationCreate, default_model: str
) -> Conversation:
    conv = Conversation(
        user_id=user_id,
        title=payload.title,
        model=payload.model or default_model,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def list_conversations(
    db: AsyncSession, user_id: str, include_archived: bool = False
) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    if not include_archived:
        stmt = stmt.where(Conversation.is_archived == False)  # noqa: E712
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_conversation(
    db: AsyncSession, conv_id: str, user_id: str
) -> Conversation | None:
    stmt = select(Conversation).where(
        Conversation.id == conv_id, Conversation.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_conversation(
    db: AsyncSession, conv_id: str, user_id: str, payload: ConversationUpdate
) -> Conversation | None:
    conv = await get_conversation(db, conv_id, user_id)
    if not conv:
        return None
    updates = payload.model_dump(exclude_none=True)
    for key, val in updates.items():
        setattr(conv, key, val)
    await db.commit()
    await db.refresh(conv)
    return conv


async def delete_conversation(db: AsyncSession, conv_id: str, user_id: str) -> bool:
    conv = await get_conversation(db, conv_id, user_id)
    if not conv:
        return False
    await db.delete(conv)
    await db.commit()
    return True
