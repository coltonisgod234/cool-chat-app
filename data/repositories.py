import json
from sqlalchemy.orm import Session
from .database import Database
from ..domain.models import User, Guild, Channel, Message
from ..service import utils

INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG = utils.get_loglevels()

class BaseRepository:
    def __init__(self, database: Database):
        self._db = database

    def _get_session(self) -> Session:
        """Provides a new session from the database manager."""
        return self._db.get_session()

    def _commit_session(self, session: Session):
        """Commits and closes the session using the database manager."""
        self._db.commit_session(session)

    def _close_session(self, session: Session):
        """Closes the session without committing, using the database manager."""
        self._db.close_session(session)


class UserRepository(BaseRepository):
    def get_user_by_cid(self, cid: str) -> User | None:
        session = self._get_session()
        try:
            return session.query(User).filter(User.cid == cid).first()
        finally:
            self._close_session(session)

    def get_user_by_username(self, username: str) -> User | None:
        session = self._get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            self._close_session(session)

    def get_user_by_token(self, token: str) -> User | None:
        session = self._get_session()
        try:
            if not token:  # Ensure token is not empty or None before querying
                return None
            return session.query(User).filter(User.token == token).first()
        finally:
            self._close_session(session)

    def create_user(self, username: str, token: str | None = None) -> User | None:
        session = self._get_session()
        try:
            cid = utils.generate_id()
            new_user = User(cid=cid, username=username, token=token)
            session.add(new_user)
            self._commit_session(session)
            return self.get_user_by_username(username)  # Return a fresh copy from DB
        except Exception as e:
            utils.log(ERROR, f"Error creating user: {e}")
            session.rollback()
            return None

    def update_user_token(self, cid: str, token: str | None) -> bool:
        session = self._get_session()
        try:
            user = session.query(User).filter(User.cid == cid).first()
            if user:
                user.token = token
                self._commit_session(session)
                return True
            return False
        except Exception as e:
            utils.log(ERROR, f"Error updating user token: {e}")
            session.rollback()
            return False

    def delete_user(self, cid: str) -> bool:
        session = self._get_session()
        try:
            user = session.query(User).filter(User.cid == cid).first()
            if user:
                session.delete(user)
                self._commit_session(session)
                return True
            return False
        except Exception as e:
            utils.log(ERROR, f"Error deleting user: {e}")
            session.rollback()
            return False


class GuildRepository(BaseRepository):
    def get_guild_by_cid(self, cid: str) -> Guild | None:
        session = self._get_session()
        try:
            return session.query(Guild).filter(Guild.cid == cid).first()
        finally:
            self._close_session(session)

    def create_guild(self, initial_permissions: dict | None = None) -> Guild:
        session = self._get_session()
        try:
            cid = utils.generate_id()
            permissions_json_str = json.dumps(initial_permissions) if initial_permissions else None
            new_guild = Guild(cid=cid, permissions_json=permissions_json_str)
            session.add(new_guild)
            self._commit_session(session)
            return new_guild
        except Exception as e:
            utils.log(ERROR, f"Error creating guild: {e}")
            session.rollback()
            raise

    def update_guild_permissions(self, cid: str, permissions: dict) -> Guild | None:
        session = self._get_session()
        try:
            guild = session.query(Guild).filter(Guild.cid == cid).first()
            if guild:
                guild.permissions_json = json.dumps(permissions)
                self._commit_session(session)
                return guild
            return None
        except Exception as e:
            utils.log(ERROR, f"Error updating guild permissions: {e}")
            session.rollback()
            raise

    def get_guild_permissions(self, cid: str) -> dict | None:
        session = self._get_session()
        try:
            guild = session.query(Guild).filter(Guild.cid == cid).first()
            if guild and guild.permissions_json:
                return json.loads(guild.permissions_json)
            return None  # Or {} if you prefer empty dict for no permissions
        finally:
            self._close_session(session)

    def delete_guild(self, cid: str) -> bool:
        session = self._get_session()
        try:
            guild = session.query(Guild).filter(Guild.cid == cid).first()
            if guild:
                session.delete(guild)
                self._commit_session(session)
                return True
            return False
        except Exception as e:
            utils.log(ERROR, f"Error deleting guild: {e}")
            session.rollback()
            raise


class ChannelRepository(BaseRepository):
    def get_channel_by_cid(self, cid: str) -> Channel | None:
        session = self._get_session()
        try:
            return session.query(Channel).filter(Channel.cid == cid).first()
        finally:
            self._close_session(session)

    def create_channel(self, guild_id: str, name: str, permissions_json: str | None = None) -> Channel:
        session = self._get_session()
        try:
            cid = utils.generate_id()
            new_channel = Channel(
                cid=cid, 
                name=name,
                guild_id=guild_id,
                permissions_json=permissions_json
            )
            session.add(new_channel)
            self._commit_session(session)
            return new_channel
        except Exception as e:
            utils.log(ERROR, f"Error creating channel: {e}")
            session.rollback()
            raise

    def get_channels_by_guild_id(self, guild_id: str) -> list[Channel]:
        session = self._get_session()
        try:
            return session.query(Channel).filter(Channel.guild_id == guild_id).all()
        finally:
            self._close_session(session)

    def delete_channel(self, cid: str) -> bool:
        session = self._get_session()
        try:
            channel = session.query(Channel).filter(Channel.cid == cid).first()
            if channel:
                session.delete(channel)
                self._commit_session(session)
                return True
            return False
        except Exception as e:
            utils.log(ERROR, f"Error deleting channel: {e}")
            session.rollback()
            raise


class MessageRepository(BaseRepository):
    def get_message_by_cid(self, cid: str) -> Message | None:
        session = self._get_session()
        try:
            return session.query(Message).filter(Message.cid == cid).first()
        finally:
            self._close_session(session)

    def create_message(self, author_cid: str, channel_cid: str, content: str, timestamp: str | None = None) -> Message:
        session = self._get_session()
        try:
            if timestamp is None:
                timestamp = str(utils.get_timestamp())
                
            cid = utils.generate_id()
            new_message = Message(
                cid=cid,
                author_cid=author_cid,
                channel_cid=channel_cid,
                content=content,
                timestamp=timestamp
            )
            session.add(new_message)
            self._commit_session(session)
            return new_message
        except Exception as e:
            utils.log(ERROR, f"Error creating message: {e}")
            session.rollback()
            raise

    def get_messages_by_channel_cid(self, channel_cid: str, limit: int = 50, offset: int = 0) -> list[Message]:
        session = self._get_session()
        try:
            messages = (
                session.query(Message)
                .filter(Message.channel_cid == channel_cid)
                .order_by(Message.timestamp.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            return messages
        finally:
            self._close_session(session)
            
    def update_message_content(self, cid: str, new_content: str) -> Message | None:
        session = self._get_session()
        try:
            message = session.query(Message).filter(Message.cid == cid).first()
            if message:
                message.content = new_content
                self._commit_session(session)
                return message
            return None
        except Exception as e:
            utils.log(ERROR, f"Error updating message content: {e}")
            session.rollback()
            raise
            
    def delete_message(self, cid: str) -> bool:
        session = self._get_session()
        try:
            message = session.query(Message).filter(Message.cid == cid).first()
            if message:
                session.delete(message)
                self._commit_session(session)
                return True
            return False
        except Exception as e:
            utils.log(ERROR, f"Error deleting message: {e}")
            session.rollback()
            raise 