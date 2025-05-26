import json
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from .mongo_database import MongoDatabase
from domain.models import User, Guild, Channel, Message
from service import utils

INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG = utils.get_loglevels()

class BaseMongoRepository:
    def __init__(self, database: MongoDatabase):
        self._db = database

class UserMongoRepository(BaseMongoRepository):
    def get_user_by_cid(self, cid: str) -> User | None:
        try:
            collection = self._db.get_user_collection()
            user_data = collection.find_one({"cid": cid})
            if not user_data:
                return None
            return User(cid=user_data["cid"], username=user_data["username"], token=user_data.get("token"))
        except Exception as e:
            utils.log(ERROR, f"Error getting user by cid: {e}")
            return None

    def get_user_by_username(self, username: str) -> User | None:
        try:
            collection = self._db.get_user_collection()
            user_data = collection.find_one({"username": username})
            if not user_data:
                return None
            return User(cid=user_data["cid"], username=user_data["username"], token=user_data.get("token"))
        except Exception as e:
            utils.log(ERROR, f"Error getting user by username: {e}")
            return None

    def get_user_by_token(self, token: str) -> User | None:
        try:
            if not token:  # Ensure token is not empty or None before querying
                return None
            collection = self._db.get_user_collection()
            user_data = collection.find_one({"token": token})
            if not user_data:
                return None
            return User(cid=user_data["cid"], username=user_data["username"], token=user_data.get("token"))
        except Exception as e:
            utils.log(ERROR, f"Error getting user by token: {e}")
            return None

    def create_user(self, username: str, token: str | None = None) -> User | None:
        try:
            # Check if user already exists first to match SQL behavior
            existing_user = self.get_user_by_username(username)
            if existing_user:
                return None
                
            collection = self._db.get_user_collection()
            cid = utils.generate_id()
            new_user = {
                "cid": cid,
                "username": username,
                "token": token
            }
            collection.insert_one(new_user)
            return self.get_user_by_username(username)  # Return a fresh copy from DB
        except DuplicateKeyError:
            # Handle duplicate username error (unique index violation)
            utils.log(ERROR, f"Error creating user: Username {username} already exists")
            return None
        except Exception as e:
            utils.log(ERROR, f"Error creating user: {e}")
            return None

    def update_user_token(self, cid: str, token: str | None) -> bool:
        try:
            collection = self._db.get_user_collection()
            result = collection.update_one(
                {"cid": cid},
                {"$set": {"token": token}}
            )
            return result.modified_count > 0
        except Exception as e:
            utils.log(ERROR, f"Error updating user token: {e}")
            return False

    def delete_user(self, cid: str) -> bool:
        try:
            collection = self._db.get_user_collection()
            result = collection.delete_one({"cid": cid})
            return result.deleted_count > 0
        except Exception as e:
            utils.log(ERROR, f"Error deleting user: {e}")
            return False


class GuildMongoRepository(BaseMongoRepository):
    def get_guild_by_cid(self, cid: str) -> Guild | None:
        try:
            collection = self._db.get_guild_collection()
            guild_data = collection.find_one({"cid": cid})
            if not guild_data:
                return None
            
            guild = Guild(
                cid=guild_data["cid"],
                permissions_json=guild_data.get("permissions_json")
            )
            return guild
        except Exception as e:
            utils.log(ERROR, f"Error getting guild by cid: {e}")
            return None

    def create_guild(self, initial_permissions: dict | None = None) -> Guild:
        try:
            collection = self._db.get_guild_collection()
            cid = utils.generate_id()
            permissions_json = json.dumps(initial_permissions) if initial_permissions else None
            new_guild = {
                "cid": cid,
                "permissions_json": permissions_json
            }
            collection.insert_one(new_guild)
            return Guild(cid=cid, permissions_json=permissions_json)
        except Exception as e:
            utils.log(ERROR, f"Error creating guild: {e}")
            raise

    def update_guild_permissions(self, cid: str, permissions: dict) -> Guild | None:
        try:
            collection = self._db.get_guild_collection()
            permissions_json = json.dumps(permissions)
            result = collection.update_one(
                {"cid": cid},
                {"$set": {"permissions_json": permissions_json}}
            )
            if result.modified_count > 0:
                return Guild(cid=cid, permissions_json=permissions_json)
            return None
        except Exception as e:
            utils.log(ERROR, f"Error updating guild permissions: {e}")
            raise

    def get_guild_permissions(self, cid: str) -> dict | None:
        try:
            collection = self._db.get_guild_collection()
            guild_data = collection.find_one({"cid": cid})
            if guild_data and guild_data.get("permissions_json"):
                return json.loads(guild_data["permissions_json"])
            return None
        except Exception as e:
            utils.log(ERROR, f"Error getting guild permissions: {e}")
            return None

    def delete_guild(self, cid: str) -> bool:
        try:
            collection = self._db.get_guild_collection()
            result = collection.delete_one({"cid": cid})
            return result.deleted_count > 0
        except Exception as e:
            utils.log(ERROR, f"Error deleting guild: {e}")
            raise


class ChannelMongoRepository(BaseMongoRepository):
    def get_channel_by_cid(self, cid: str) -> Channel | None:
        try:
            collection = self._db.get_channel_collection()
            channel_data = collection.find_one({"cid": cid})
            if not channel_data:
                return None
            
            channel = Channel(
                cid=channel_data["cid"],
                name=channel_data["name"],
                guild_id=channel_data["guild_id"],
                permissions_json=channel_data.get("permissions_json")
            )
            return channel
        except Exception as e:
            utils.log(ERROR, f"Error getting channel by cid: {e}")
            return None

    def create_channel(self, guild_id: str, name: str, permissions_json: str | None = None) -> Channel:
        try:
            collection = self._db.get_channel_collection()
            cid = utils.generate_id()
            new_channel = {
                "cid": cid,
                "name": name,
                "guild_id": guild_id,
                "permissions_json": permissions_json
            }
            collection.insert_one(new_channel)
            return Channel(
                cid=cid,
                name=name,
                guild_id=guild_id,
                permissions_json=permissions_json
            )
        except Exception as e:
            utils.log(ERROR, f"Error creating channel: {e}")
            raise

    def get_channels_by_guild_id(self, guild_id: str) -> list[Channel]:
        try:
            collection = self._db.get_channel_collection()
            channels_data = collection.find({"guild_id": guild_id})
            
            channels = []
            for channel_data in channels_data:
                channel = Channel(
                    cid=channel_data["cid"],
                    name=channel_data["name"],
                    guild_id=channel_data["guild_id"],
                    permissions_json=channel_data.get("permissions_json")
                )
                channels.append(channel)
            
            return channels
        except Exception as e:
            utils.log(ERROR, f"Error getting channels by guild id: {e}")
            return []

    def delete_channel(self, cid: str) -> bool:
        try:
            collection = self._db.get_channel_collection()
            result = collection.delete_one({"cid": cid})
            return result.deleted_count > 0
        except Exception as e:
            utils.log(ERROR, f"Error deleting channel: {e}")
            raise


class MessageMongoRepository(BaseMongoRepository):
    def get_message_by_cid(self, cid: str) -> Message | None:
        try:
            collection = self._db.get_message_collection()
            message_data = collection.find_one({"cid": cid})
            if not message_data:
                return None
            
            message = Message(
                cid=message_data["cid"],
                author_cid=message_data["author_cid"],
                channel_cid=message_data["channel_cid"],
                content=message_data["content"],
                timestamp=message_data["timestamp"]
            )
            return message
        except Exception as e:
            utils.log(ERROR, f"Error getting message by cid: {e}")
            return None

    def create_message(self, author_cid: str, channel_cid: str, content: str, timestamp: str | None = None) -> Message:
        try:
            collection = self._db.get_message_collection()
            
            if timestamp is None:
                timestamp = str(utils.get_timestamp())
                
            cid = utils.generate_id()
            new_message = {
                "cid": cid,
                "author_cid": author_cid,
                "channel_cid": channel_cid,
                "content": content,
                "timestamp": timestamp
            }
            collection.insert_one(new_message)
            
            message = Message(
                cid=cid,
                author_cid=author_cid,
                channel_cid=channel_cid,
                content=content,
                timestamp=timestamp
            )
            return message
        except Exception as e:
            utils.log(ERROR, f"Error creating message: {e}")
            raise

    def get_messages_by_channel_cid(self, channel_cid: str, limit: int = 50, offset: int = 0) -> list[Message]:
        try:
            collection = self._db.get_message_collection()
            messages_data = collection.find(
                {"channel_cid": channel_cid}
            ).sort("timestamp", -1).skip(offset).limit(limit)
            
            messages = []
            for message_data in messages_data:
                message = Message(
                    cid=message_data["cid"],
                    author_cid=message_data["author_cid"],
                    channel_cid=message_data["channel_cid"],
                    content=message_data["content"],
                    timestamp=message_data["timestamp"]
                )
                messages.append(message)
            
            return messages
        except Exception as e:
            utils.log(ERROR, f"Error getting messages by channel cid: {e}")
            return []
            
    def update_message_content(self, cid: str, new_content: str) -> Message | None:
        try:
            collection = self._db.get_message_collection()
            result = collection.update_one(
                {"cid": cid},
                {"$set": {"content": new_content}}
            )
            if result.modified_count > 0:
                return self.get_message_by_cid(cid)
            return None
        except Exception as e:
            utils.log(ERROR, f"Error updating message content: {e}")
            raise
            
    def delete_message(self, cid: str) -> bool:
        try:
            collection = self._db.get_message_collection()
            result = collection.delete_one({"cid": cid})
            return result.deleted_count > 0
        except Exception as e:
            utils.log(ERROR, f"Error deleting message: {e}")
            raise 