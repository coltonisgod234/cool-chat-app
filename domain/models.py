from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, select
from sqlalchemy.orm import relationship
from data.database import Base, Database
from service import utils

INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG = utils.get_loglevels()

# Data models for ORM
class User(Base):
    __tablename__ = "user"

    cid = Column(String, primary_key=True)
    token = Column(String, nullable=True)
    username = Column(String)
    password_hash = Column(String, nullable=True)

    def copy_user_data(self, user_data_source):
        self.cid = user_data_source.cid
        self.token = user_data_source.token
        self.username = user_data_source.username
        self.password_hash = user_data_source.password_hash
    
    def __repr__(self):
        return f'User(cid={self.cid}, username={self.username})'

class Guild(Base):
    __tablename__ = "guild"

    cid = Column(String, primary_key=True)
    channels = relationship("Channel", back_populates="guild")
    permissions_json = Column(String, nullable=True)

    def copy_guild_data(self, guild_data_source):
        self.cid = guild_data_source.cid
        self.permissions_json = guild_data_source.permissions_json
        
    def __repr__(self):
        return f'Guild(cid={self.cid})'

class Channel(Base):
    __tablename__ = "channel"

    name = Column(String)
    cid = Column(String, primary_key=True)

    messages = relationship("Message", back_populates="channel")
    guild_id = Column(ForeignKey("guild.cid"))
    guild = relationship("Guild", back_populates="channels")
    
    permissions_json = Column(String, nullable=True)

    def copy_channel_data(self, channel_data_source):
        self.cid = channel_data_source.cid
        self.permissions_json = channel_data_source.permissions_json
        
    def __repr__(self):
        return f'Channel(cid={self.cid}, name={self.name})'

class Message(Base):
    __tablename__ = "message"

    cid = Column(String, primary_key=True)
    
    author_cid = Column(ForeignKey("user.cid"))
    author = relationship("User")
    
    channel_cid = Column(ForeignKey("channel.cid"))
    channel = relationship("Channel", back_populates="messages")

    timestamp = Column(String)
    content = Column(String)
    
    def __repr__(self):
        return f'Message(cid={self.cid}, from={self.author}, content={self.content}, at={self.timestamp})'

# In-memory models (for chat_logic)
class InMemoryMessage:
    def __init__(self, author, content, timestamp, cid=utils.generate_id()):
        self.author = author
        self.content = content
        self.timestamp = timestamp
        self.cid = cid
    
    def __repr__(self):
        return f'Message(cid={self.cid}, from={self.author}, content={self.content}, at={self.timestamp})'

class InMemoryChannel:
    def __init__(self, name:str, cid=utils.generate_id()):
        self.cid = cid
        self.messages = {}
        self.permissions = {}
        self.name = name
    
    def __repr__(self):
        return f'Channel(cid={self.cid}, name={self.name})'

    def add_message(self, msg:InMemoryMessage):
        '''
        Add message without authentication
        '''
        self.messages[msg.cid] = msg
        return msg

    def delete_message(self, cid):
        '''
        Delete a message without authentication
        '''
        del self.messages[cid]
        
    def edit_message(self, cid, newMsg:InMemoryMessage):
        '''
        Edit a message without authentication
        '''
        self.messages[cid] = newMsg
        
    def authorized_add_message(self, msg:InMemoryMessage, token):
        '''
        Add a message WITH authentication
        '''
        username = msg.author.username

        # Ensure the user is authenticated
        if not msg.author.token_auth(token):
            raise PermissionError("Bad token")

        # Ensure they have permission
        if not utils.check_permission(self, username, "send_messages"):
            raise PermissionError("You do not have the required permission 'send_messages'")
        
        return self.add_message(msg)
    
class InMemoryGuild:
    def __init__(self, cid=utils.generate_id()):
        self.cid = cid
        self.channels = {}
        self.permissions = {}
    
    def __repr__(self):
        return f'Guild(cid={self.cid})'
    
    def add_channel(self, ch:InMemoryChannel):
        '''
        Attach a given Channel object `ch` to this guild
        '''
        self.channels[ch.cid] = ch
        
    def delete_channel(self, cid):
        '''
        Detatch the channel with the given CID from this guild
        '''
        del self.channels[cid] 