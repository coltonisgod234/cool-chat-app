"""
Testing utilities for MongoDB in the chat application.
These functions should ONLY be used in tests, never in production code.
"""
from data.mongo_database import MongoDatabase

class MongoDBCleaner:
    """Utility class for cleaning up test data in MongoDB.
    This should only be used in test environments, never in production."""
    
    def __init__(self, db: MongoDatabase):
        self._db = db
        
    def clear_all_messages(self) -> bool:
        """Delete all messages from the database."""
        try:
            collection = self._db.get_message_collection()
            collection.delete_many({})
            return True
        except Exception as e:
            print(f"Error during MongoDB test cleanup: {e}")
            return False
    
    def clear_all_channels(self) -> bool:
        """Delete all channels from the database."""
        try:
            collection = self._db.get_channel_collection()
            collection.delete_many({})
            return True
        except Exception as e:
            print(f"Error during MongoDB test cleanup: {e}")
            return False
    
    def clear_all_guilds(self) -> bool:
        """Delete all guilds from the database."""
        try:
            collection = self._db.get_guild_collection()
            collection.delete_many({})
            return True
        except Exception as e:
            print(f"Error during MongoDB test cleanup: {e}")
            return False
    
    def clear_all_users_except_default(self) -> bool:
        """Delete all users except the default one (colton)."""
        try:
            collection = self._db.get_user_collection()
            collection.delete_many({"username": {"$ne": "colton"}})
            return True
        except Exception as e:
            print(f"Error during MongoDB test cleanup: {e}")
            return False
    
    def reset_database(self) -> bool:
        """Reset the entire database to a clean state.
        Preserves only the default user (colton)."""
        # Drop and recreate all collections
        self._db.drop_all_collections()
        self._db.create_tables()
        return True 