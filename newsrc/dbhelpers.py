from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from contextlib import contextmanager
import utils
from typing import Optional, List

INFO, WARN, ERROR, CRITICAL = utils.get_loglevels()

Base = declarative_base()
engine = create_engine('sqlite:///example.db', echo=True)
SessionLocal = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    token = Column(String, nullable=True)
    password = Column(String)
    username = Column(String, unique=True)

    @classmethod
    def create(cls, username: str, password: str, cid: str) -> 'User':
        with get_session() as session:
            if session.query(cls).filter((cls.id == cid) | (cls.username == username)).first():
                utils.log(WARN, f"User {username} already exists")
                return None
            user = cls(id=cid, username=username, password=password)
            session.add(user)
            return user

    @classmethod
    def get(cls, user_id: str = None, username: str = None) -> Optional['User']:
        with get_session() as session:
            if user_id:
                return session.query(cls).filter(cls.id == user_id).first()
            elif username:
                return session.query(cls).filter(cls.username == username).first()
        return None

    def update_token(self, token: str) -> None:
        with get_session() as session:
            user = session.query(User).filter(User.id == self.id).first()
            if user:
                user.token = token

class Message(Base):
    __tablename__ = "message"

    id = Column(String, primary_key=True)
    content = Column(String)
    channel_id = Column(String, ForeignKey('channel.id'))
    channel = relationship("Channel", back_populates="messages")

    @classmethod
    def create(cls, content: str, channel_id: str, cid: str) -> 'Message':
        with get_session() as session:
            msg = cls(id=cid, content=content, channel_id=channel_id)
            session.add(msg)
            return msg

    @classmethod
    def delete(cls, msg_id: str) -> bool:
        with get_session() as session:
            msg = session.query(cls).filter(cls.id == msg_id).first()
            if msg:
                session.delete(msg)
                return True
            return False

    def edit(self, new_content: str) -> None:
        with get_session() as session:
            msg = session.query(Message).filter(Message.id == self.id).first()
            if msg:
                msg.content = new_content

class Channel(Base):
    __tablename__ = "channel"

    id = Column(String, primary_key=True)
    name = Column(String)
    guild_id = Column(String, ForeignKey('guild.id'))
    guild = relationship("Guild", back_populates="channels")
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")

    @classmethod
    def create(cls, name: str, guild_id: str, cid: str) -> 'Channel':
        with get_session() as session:
            channel = cls(id=cid, name=name, guild_id=guild_id)
            session.add(channel)
            return channel

    @classmethod
    def delete(cls, channel_id: str) -> bool:
        with get_session() as session:
            channel = session.query(cls).filter(cls.id == channel_id).first()
            if channel:
                session.delete(channel)
                return True
            return False

    def add_message(self, msg: Message) -> None:
        with get_session() as session:
            channel = session.query(Channel).filter(Channel.id == self.id).first()
            if channel:
                channel.messages.append(msg)

class Guild(Base):
    __tablename__ = "guild"

    id = Column(String, primary_key=True)
    channels = relationship("Channel", back_populates="guild", cascade="all, delete-orphan")

    @classmethod
    def create(cls, cid: str) -> 'Guild':
        with get_session() as session:
            guild = cls(id=cid)
            session.add(guild)
            return guild

    @classmethod
    def delete(cls, guild_id: str) -> bool:
        with get_session() as session:
            guild = session.query(cls).filter(cls.id == guild_id).first()
            if guild:
                session.delete(guild)
                return True
            return False

    def add_channel(self, channel: Channel) -> None:
        with get_session() as session:
            guild = session.query(Guild).filter(Guild.id == self.id).first()
            if guild:
                guild.channels.append(channel)