from enum import Enum
from typing import Tuple, Type

from .database import Database
from .mongo_database import MongoDatabase
from .repositories import UserRepository, GuildRepository, ChannelRepository, MessageRepository
from .mongo_repositories import UserMongoRepository, GuildMongoRepository, ChannelMongoRepository, MessageMongoRepository

class DBType(Enum):
    SQL = "sql"
    MONGO = "mongo"

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: DBType = DBType.SQL, **kwargs) -> Tuple:
        """
        Create database and repositories based on the database type.
        
        Args:
            db_type: The type of database to create (SQL or MongoDB)
            **kwargs: Additional configuration options for the database

        Returns:
            Tuple containing (database, user_repo, guild_repo, channel_repo, message_repo)
        """
        if db_type == DBType.SQL:
            db_url = kwargs.get("db_url", "sqlite:///new_web_server.db")
            echo = kwargs.get("echo", False)
            
            db = Database(db_url=db_url, echo=echo)
            db.create_tables()
            
            user_repo = UserRepository(db)
            guild_repo = GuildRepository(db)
            channel_repo = ChannelRepository(db)
            message_repo = MessageRepository(db)
            
        elif db_type == DBType.MONGO:
            connection_uri = kwargs.get("connection_uri", "mongodb://localhost:27017/")
            db_name = kwargs.get("db_name", "cool_chat_app")
            
            db = MongoDatabase(connection_uri=connection_uri, db_name=db_name)
            db.create_tables()  # Creates indexes for MongoDB
            
            user_repo = UserMongoRepository(db)
            guild_repo = GuildMongoRepository(db)
            channel_repo = ChannelMongoRepository(db)
            message_repo = MessageMongoRepository(db)
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
            
        return db, user_repo, guild_repo, channel_repo, message_repo 