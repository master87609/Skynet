"""
Message Log Service — saves chat messages to MongoDB.
"""
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.schemas import MessageLogCreate


COLLECTION = "messages"


async def save_message(db: AsyncIOMotorDatabase, msg: MessageLogCreate) -> str:
    doc = {
        "conversation_id": msg.conversation_id,
        "user_id": msg.user_id,
        "role": msg.role,
        "content": msg.content,
        "model": msg.model,
        "tokens": msg.tokens or 0,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db[COLLECTION].insert_one(doc)
    return str(result.inserted_id)


async def get_messages(
    db: AsyncIOMotorDatabase,
    conversation_id: str,
    limit: int = 100,
) -> list[dict]:
    cursor = (
        db[COLLECTION]
        .find({"conversation_id": conversation_id})
        .sort("created_at", 1)
        .limit(limit)
    )
    messages = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        messages.append(doc)
    return messages


async def delete_messages_for_conversation(
    db: AsyncIOMotorDatabase, conversation_id: str
) -> int:
    result = await db[COLLECTION].delete_many({"conversation_id": conversation_id})
    return result.deleted_count
