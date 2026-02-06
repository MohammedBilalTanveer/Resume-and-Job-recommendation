from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from backend.config import settings
from typing import Optional

# MongoDB client instances
_async_client: Optional[AsyncIOMotorClient] = None
_sync_client: Optional[MongoClient] = None


def get_sync_client() -> MongoClient:
    """Get synchronous MongoDB client (for startup/shutdown)."""
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(settings.MONGODB_URL)
    return _sync_client


def get_async_client() -> AsyncIOMotorClient:
    """Get async MongoDB client."""
    global _async_client
    if _async_client is None:
        _async_client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _async_client


def get_database():
    """Get the database instance (async)."""
    client = get_async_client()
    return client[settings.MONGODB_DB_NAME]


def get_sync_database():
    """Get the database instance (sync)."""
    client = get_sync_client()
    return client[settings.MONGODB_DB_NAME]


# Collection getters
def get_users_collection():
    """Get users collection."""
    return get_database()["users"]


def get_analyses_collection():
    """Get resume analyses collection."""
    return get_database()["resume_analyses"]


def get_counters_collection():
    """Get counters collection for auto-increment IDs."""
    return get_database()["counters"]


async def get_next_sequence(name: str) -> int:
    """Get next sequence number for auto-increment IDs."""
    counters = get_counters_collection()
    result = await counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return result["seq"]


async def init_database():
    """Initialize database with indexes."""
    db = get_database()
    
    # Create indexes for users collection
    users = db["users"]
    await users.create_index("email", unique=True)
    await users.create_index([("oauth_provider", 1), ("oauth_id", 1)])
    
    # Create indexes for resume_analyses collection
    analyses = db["resume_analyses"]
    await analyses.create_index("user_id")
    await analyses.create_index([("user_id", 1), ("created_at", -1)])
    
    # Initialize counters if they don't exist
    counters = db["counters"]
    await counters.update_one(
        {"_id": "users"},
        {"$setOnInsert": {"seq": 0}},
        upsert=True
    )
    await counters.update_one(
        {"_id": "resume_analyses"},
        {"$setOnInsert": {"seq": 0}},
        upsert=True
    )
    
    print("[OK] MongoDB indexes created")


def close_connections():
    """Close MongoDB connections."""
    global _async_client, _sync_client
    if _async_client:
        _async_client.close()
        _async_client = None
    if _sync_client:
        _sync_client.close()
        _sync_client = None

