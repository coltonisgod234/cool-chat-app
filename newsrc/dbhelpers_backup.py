from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import utils

INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG = utils.get_loglevels()
DB_PATH = "sqlite:///example.db"

Base = declarative_base()
engine = create_engine(DB_PATH, echo=False)

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

    user_id = Column(String, ForeignKey('users.id'))

    channel_id = Column(String, ForeignKey('channel.id'))  # ForeignKey to Channel
    channel = relationship("Channel", back_populates="messages")

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

class DatabaseManagement:
    '''
    Common methods for database management wrapped into a class

    This class is DEPENDENT on the rest of this file.
    '''
    def __init__(self, filepath):
        self.database_file = filepath

    def check_user_exists(self, u):
        # We want to check if the user exists
        session = new_session()
        occurences = session.query(User).filter(User.id == u.cid).all()  # If this reutnrs an empty array, there's no conflict
        just_close(session)

        if occurences != []:
            return True  # The user doesn't exist
        else:
            return False  # The user exists
    
    def check_guild_exists(self, guild):
        session = new_session()
        occurences = session.query(Guild).filter(Guild.id == guild.cid).all()
        just_close(session)
        
        if occurences != []:
            return True
        else:
            return False
    
    def check_channel_exists(self, ch):
        session = new_session()
        occurences = session.query(Channel).filter(Channel.id == ch.cid).all()
        just_close(session)
        
        if occurences != []:
            return True
        else:
            return False
    
    def get_guild(self, guild):
        session = new_session()
        data = session.query(Guild).filter(Guild.id == guild.cid).first()
        #just_close(session)
        return data

    def get_channel(self, ch):
        session = new_session()
        data = session.query(Channel).filter(Channel.id == ch.cid).first()
        #just_close(session)
        return data
    
    def get_user(self, user):
        session = new_session()
        data = session.query(User).filter(User.id == user.cid).first()
        #just_close(session)
        return data

    def add_user(self, u):
        session = new_session()

        # We want to check if the user exists
        if self.check_user_exists(u):
            return

        usr = User(id=u.cid, username=u.username, password=u.password)

        session.add(usr)

        commit_close(session)
        return        

    def del_user(self, user, index=0):
        session = new_session()

        # Make sure they exist, we can't delete nothing after all
        if not self.check_user_exists(user):
            return
        
        # Otherwise, we're good to delete them
        # First, query to find the user
        foundusers = session.query(User).filter(User.id == user.cid).all()
        user = utils.try_index(foundusers, index)

        # Now use the session to delete the user
        session.delete(user)

        commit_close(session)
        return
    
    def add_guild(self, guild):
        session = new_session()

        # Make sure the guild doesn't already exist
        if self.check_guild_exists(guild):
            return
        
        g = Guild(id=guild.cid)
        session.add(g)

        commit_close(session)
        return

    def add_channel(self, ch):
        session = new_session()

        if self.check_channel_exists(ch):
            return
        
        c = Channel(id=ch.cid)
        session.add(c)

        commit_close(session)
        return
    
    def attach_channel(self, ch, guild):
        session = new_session()

        if not self.check_channel_exists(ch):  # Channel must exist
            return

        if not self.check_guild_exists(guild):  # Guild must exist
            return
        
        c = self.get_channel(ch)
        g = self.get_guild(guild)
        g.channels.append(c)

        commit_close(session)
        return
    
    def attach_message(self, ch, msg):
        '''
        Attaches an existing message to a channel
        '''
        session = new_session()

        if not self.check_channel_exists(ch):  # Channel must exist
            return
        
        c = self.get_channel(ch)
        c.messages.append(msg)

        commit_close(session)
        
        return

    def add_message(self, msg):
        '''
        Adds a messages.Message object to the database
        '''
        session = new_session()

        u = self.get_user(msg.author)
        m = Message(id=msg.cid, content=msg.content, user_id=u)

        session.add(m)
        commit_close(session)
        
        return
