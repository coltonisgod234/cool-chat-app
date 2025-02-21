from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import utils

INFO, WARN, ERROR, CRITICAL = utils.get_loglevels()

Base = declarative_base()
engine = create_engine('sqlite:///example.db', echo=True)

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    token = Column(String, nullable=True)
    password = Column(String)  # FOR TESTING SAKE!!
    username = Column(String)

class Channel(Base):
    __tablename__ = "channel"

    id = Column(String, primary_key=True)
    guild_id = Column(String, ForeignKey('guild.id'))  # ForeignKey to Guild
    guild = relationship("Guild", back_populates="channels")
    messages = relationship("Message", back_populates="channel")

class Guild(Base):
    __tablename__ = "guild"

    id = Column(String, primary_key=True)
    channels = relationship("Channel", back_populates="guild")

class Message(Base):
    __tablename__ = "message"

    id = Column(String, primary_key=True)
    content = Column(String)
    channel_id = Column(String, ForeignKey('channel.id'))  # ForeignKey to Channel
    channel = relationship("Channel", back_populates="messages")

def new_session():
    utils.log(INFO, "Creating new database session...")
    s = sessionmaker(bind=engine)
    session = s()
    return session

def add_user(u):
    utils.log(INFO, f"Creating database entry for user {u.username}")
    session = new_session()

    # We want to check if the user exists
    utils.log(INFO, "Checking for conflicts...")
    occurences = session.query(User).filter(User.id == u.cid or User.username == u.username).all()
    if occurences != []:
        utils.log(WARN, f"User with CID {u.cid} ({u.username}) already exists in database! Refusing to recreate it. occurences: {occurences} ({len(occurences)} total)")
        return

    utils.log(INFO, "No conflicts!")
    usr = User(id=u.cid, username=u.username, password=u.password)
    session.add(usr)
    session.commit()
    utils.log(INFO, "Success!")
    session.close()