"""
MongoDB connection management.
"""

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings


@lru_cache
def get_mongo_client() -> MongoClient:
    """
    Create and cache a MongoDB client.
    """
    return MongoClient(settings.MONGODB_URI)


@lru_cache
def get_database() -> Database:
    """
    Return the configured MongoDB database.
    """
    client = get_mongo_client()
    return client[settings.DATABASE_NAME]
