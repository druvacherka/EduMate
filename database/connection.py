"""MongoDB Connection & Database Client Manager for EduMate.

Provides singleton connection handling, collection index initialization,
and database status checking.
"""

import os
import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database

logger = logging.getLogger(__name__)

# Default MongoDB configuration
DEFAULT_MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("DATABASE_URL", "mongodb://localhost:27017"))
DEFAULT_DB_NAME = os.getenv("MONGODB_DB_NAME", "edumate")


class MongoDBManager:
    """Singleton MongoDB client manager for EduMate."""

    _instance: Optional["MongoDBManager"] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        self.uri = uri or DEFAULT_MONGODB_URI
        self.db_name = db_name or DEFAULT_DB_NAME
        self._connect()

    def _connect(self):
        try:
            logger.info(f"Connecting to MongoDB at {self.uri} (database: {self.db_name})...")
            self._client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
            )
            # Test connection
            self._client.server_info()
            self._db = self._client[self.db_name]
            logger.info("MongoDB successfully connected!")
            self._init_indexes()
        except Exception as e:
            logger.warning(
                f"Failed to connect to MongoDB server ({e}). "
                f"Ensure MongoDB is running on {self.uri}."
            )
            # In case client is initialized but offline
            if self._client:
                self._db = self._client[self.db_name]

    def _init_indexes(self):
        """Create helpful collection indexes for performance and data integrity."""
        if self._db is None:
            return
        try:
            # Student Goals
            self._db.student_goals.create_index([("student_id", ASCENDING), ("is_active", DESCENDING)])
            self._db.student_goals.create_index([("priority", ASCENDING)])
            
            # Daily Tasks
            self._db.daily_study_tasks.create_index([("student_id", ASCENDING), ("date_scheduled", ASCENDING)])
            self._db.daily_study_tasks.create_index([("is_completed", ASCENDING)])

            # Study Materials
            self._db.study_materials.create_index([("upload_date", DESCENDING)])
            self._db.study_materials.create_index([("subject", ASCENDING)])

            # Revision Schedule
            self._db.revision_schedule.create_index([("student_id", ASCENDING), ("next_revision_date", ASCENDING)])
            self._db.revision_schedule.create_index([("status", ASCENDING)])

            # Study Chunks for Vector Search
            self._db.study_chunks.create_index([("document_name", ASCENDING), ("page_number", ASCENDING)])
            self._db.study_chunks.create_index([("subject", ASCENDING)])

            logger.info("MongoDB indexes successfully created.")
        except Exception as e:
            logger.warning(f"Failed to create MongoDB indexes: {e}")

    @property
    def db(self) -> Database:
        if self._db is None:
            self._connect()
        return self._db

    @property
    def client(self) -> MongoClient:
        if self._client is None:
            self._connect()
        return self._client

    def is_healthy(self) -> bool:
        """Check if MongoDB server is reachable."""
        try:
            if self._client:
                self._client.admin.command('ping')
                return True
        except Exception:
            return False
        return False


# Global singleton instance
mongo_manager = MongoDBManager()


def get_db() -> Database:
    """Return the active MongoDB database instance."""
    return mongo_manager.db


def get_client() -> MongoClient:
    """Return the active MongoClient instance."""
    return mongo_manager.client


def check_mongo_health() -> bool:
    """Return True if MongoDB is connected and healthy."""
    return mongo_manager.is_healthy()
