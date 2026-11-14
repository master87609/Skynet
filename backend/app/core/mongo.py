"""
MongoDB connection using Motor async driver.
Used for chat message logs (high-volume writes).
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_client: AsyncIOMotorClient = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URL)
    return _client


def get_mongo_db() -> AsyncIOMotorDatabase:
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]


async def close_mongo():
    global _client
    if _client:
        _client.close()
        _client = None
