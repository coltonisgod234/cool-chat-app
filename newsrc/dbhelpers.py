from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import utils

INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG = utils.get_loglevels()
DB_PATH = "sqlite:///example.db"

Base = declarative_base()
engine = create_engine(DB_PATH, echo=True)

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

class Channel(Base):
    __tablename__ = "channel"

    name = Column(String)
    cid = Column(String, primary_key=True)

    messages = relationship("Message")
    guild = relationship("Guild")
    
    permissions = ...

    def add_mesage(self, msg):
        session = new_session()
        print("Before modification", self.messages)
        self.messages.append(msg)
        print("After modification", self.messages)
        commit_close(session)

class Message(Base):
    __tablename__ = "message"

    cid = Column(String, primary_key=True)
    
    author = Column(ForeignKey("user.cid"))  # Each message has an author

    timestamp = Column(String)
    content = Column(String)

def new_session():
    utils.log(DEBUG, "Creating a new database session...")
    s = sessionmaker(bind=engine)
    session = s()
    session.expire_on_commit = False
    return session

def commit_close(session):
    utils.log(DEBUG, "Commiting changes and closing database session...")
    session.commit()
    session.close()

def just_close(session):
    utils.log(DEBUG, "Closing database session...")
    session.close()
