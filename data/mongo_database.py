from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId

class MongoDatabase:
    def __init__(self, connection_uri: str = "mongodb://localhost:27017/", 
                 db_name: str = "cool_chat_app"):
        """Initialize the MongoDB connection.

        Args:
            connection_uri: MongoDB connection URI.
            db_name: The database name to use.
        """
        self.client = MongoClient(connection_uri)
        self.db = self.client[db_name]
        
        # Define collections as properties to mimic SQL tables
        self._user_collection = self.db.users
        self._guild_collection = self.db.guilds
        self._channel_collection = self.db.channels
        self._message_collection = self.db.messages

    def create_tables(self):
        """Create indexes on collections (similar to create_all in SQLAlchemy)."""
        # Create indexes for faster lookups
        self._user_collection.create_index("username", unique=True)
        self._user_collection.create_index("token")
        self._message_collection.create_index("channel_cid")
        self._channel_collection.create_index("guild_id")

    def get_user_collection(self) -> Collection:
        """Get the users collection."""
        return self._user_collection
        
    def get_guild_collection(self) -> Collection:
        """Get the guilds collection."""
        return self._guild_collection
        
    def get_channel_collection(self) -> Collection:
        """Get the channels collection."""
        return self._channel_collection
        
    def get_message_collection(self) -> Collection:
        """Get the messages collection."""
        return self._message_collection
    
    def drop_all_collections(self):
        """Drop all collections for test cleanup."""
        self._user_collection.drop()
        self._guild_collection.drop()
        self._channel_collection.drop()
        self._message_collection.drop()
        
        # Recreate collections
        self._user_collection = self.db.users
        self._guild_collection = self.db.guilds
        self._channel_collection = self.db.channels
        self._message_collection = self.db.messages 