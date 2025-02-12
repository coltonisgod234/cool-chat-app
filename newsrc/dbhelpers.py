from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, select
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import utils

INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG = utils.get_loglevels()
DB_PATH = "sqlite:///example.db"
PREVIOUS_LOOKBACK = 2

Base = declarative_base()
engine = create_engine(DB_PATH, echo=False)

'''
Defining utility functions.
This function doesn't make sense inside User
'''
def create_user_counterpart(u):
    session = new_session()
    user = User()
    user.copy_user_data(u)

    session.add(user)
    commit_close(session)
    return user

def create_guild(cid):
    session = new_session()
    guild = Guild(cid=cid)

    session.add(guild)
    commit_close(session)
    return guild

class User(Base):
    __tablename__ = "user"

    cid = Column(String, primary_key=True)
    token = Column(String, nullable=True)
    username = Column(String)
    # No password for now, screw you

    def copy_user_data(self, user):
        self.cid = user.cid
        self.token = user.token
        self.username = user.username

    def force_logon(self, token):
        session = new_session()
        self.token = token
        commit_close(session)
    
    def force_logoff(self):
        session = new_session()
        self.token = None
        commit_close(session)

class Guild(Base):
    __tablename__ = "guild"

    cid = Column(String, primary_key=True)

    channels = relationship("Channel")

    permissions = ...

    def copy_guild_data(self, g):
        self.cid = g.cid
        self.channels = g.channels
        self.permissions = g.permissions

    def create_channel(self, channel_cid):
        session = new_session()
        channel = Channel(guild_id=self.cid, cid=channel_cid)

        session.add(channel)
        session.commit()
        #commit_close(session)
        return channel

class Channel(Base):
    __tablename__ = "channel"

    name = Column(String)
    cid = Column(String, primary_key=True)

    messages = relationship("Message")
    guild_id = Column(ForeignKey("guild.cid"))
    
    permissions = ...

    def copy_channel_data(self, ch):
        self.cid = ch.cid
        self.messages = ch.messages
        self.permissions = ch.permission

    def add_message(self, msg):
        session = new_session()
        print("Before modification", self.messages)

        author_ID = session.query(User).filter(User.cid == msg.author.cid)
        m = Message(cid=msg.cid, author=author_ID, channel=self.cid, content=msg.content)

        self.messages.append(m)
        print("After modification", self.messages)
        commit_close(session)

class Message(Base):
    __tablename__ = "message"

    cid = Column(String, primary_key=True)
    
    author = Column(ForeignKey("user.cid"))  # Each message has an author
    channel = Column(ForeignKey("channel.cid"))

    timestamp = Column(String)
    content = Column(String)

def new_session():
    utils.log(DEBUG, f"Creating a new database session, for {utils.prev_running_func(PREVIOUS_LOOKBACK)}...")
    s = sessionmaker(bind=engine)
    session = s()
    session.expire_on_commit = False
    return session

def commit_close(session):
    utils.log(DEBUG, f"Commiting changes and closing database session, for {utils.prev_running_func(PREVIOUS_LOOKBACK)}...")
    session.commit()
    session.close()

def just_close(session):
    utils.log(DEBUG, f"Closing database session, for {utils.prev_running_func(PREVIOUS_LOOKBACK)}...")
    session.close()
