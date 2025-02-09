from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import utils

INFO, WARN, ERROR, CRITICAL, VERBOSE, VERBOSEX = utils.get_loglevels()

Base = declarative_base()
engine = create_engine('sqlite:///example.db', echo=False)

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
    utils.log(INFO, "Creating new database session...")
    s = sessionmaker(bind=engine)
    session = s()
    return session

class DatabaseManagement:
    '''
    Common methods for database management wrapped into a class

    This class is DEPENDENT on the rest of this file.
    '''
    def __init__(self, filepath):
        self.database_file = filepath

    def check_user_exists(self, u, by_DB, by_GUEST):
        # We want to check if the user exists
        session = new_session()

        occurences = session.query(User).filter(getattr(User, by_DB) == getattr(u, by_GUEST)).all()  # If this reutnrs an empty array, there's no conflict

        if occurences != []:
            return True  # The user doesn't exist
        else:
            return False  # The user exists
    
    def check_guild_exists(self, guild):
        session = new_session()

        occurences = session.query(Guild).filter(Guild.id == guild.cid).all()
        
        if occurences != []:
            return True
        else:
            return False
    
    def check_channel_exists(self, ch):
        session = new_session()

        occurences = session.query(Channel).filter(Channel.id == ch.cid).all()
        
        if occurences != []:
            return True
        else:
            return False
    
    def get_guild(self, guild):
        session = new_session()
        return session.query(Guild).filter(Guild.id == guild.cid).first()

    def get_channel(self, ch):
        session = new_session()
        return session.query(Channel).filter(Channel.id == ch.cid).first()
    
    def get_user(self, user):
        session = new_session()
        return session.query(User).filter(User.id == user.cid).first()

    def add_user(self, u):
        utils.log(INFO, f"Creating database entry for user {u.username}")
        session = new_session()

        # We want to check if the user exists
        utils.log(VERBOSE, "Ensuring user doesn't already exist")
        if self.check_user_exists(u, "id", "cid"):
            utils.log(WARN, f"User {u.__repr__()} already exists. Returning early with no work done")
            return

        utils.log(VERBOSE, "Adding user...")
        utils.log(VERBOSEX, "Generating user object...")
        usr = User(id=u.cid, username=u.username, password=u.password)

        utils.log(VERBOSEX, "Appending user...")
        session.add(usr)

        utils.log(VERBOSEX, "Commiting changes...")
        session.commit()

        session.close()

    def del_user(self, user, index=0):
        utils.log(INFO, f"Deleting user with ID {user.cid} from database")
        session = new_session()

        # Make sure they exist, we can't delete nothing after all
        if not self.check_user_exists(user, "id", "cid"):
            utils.log(WARN, f"Cannot delete user {user.cid}, no such user exists. Returning early with no work done")
            return
        
        # Otherwise, we're good to delete them
        # First, query to find the user
        utils.log(VERBOSE, "Querying for this user")
        foundusers = session.query(User).filter(User.id == user.cid).all()
        
        utils.log(VERBOSEX, "Indexing...")
        user = utils.try_index(foundusers, index)

        # Now use the session to delete the user
        utils.log(VERBOSE, "Deleting the user...")
        session.delete(user)

        utils.log(VERBOSEX, "Commiting changes...")
        session.commit()

        session.close()
        return
    
    def add_guild(self, guild):
        utils.log(INFO, f"Creating record for guild on database: {guild.__repr__()}")
        session = new_session()

        # Make sure the guild doesn't already exist
        if self.check_guild_exists(guild):
            utils.log(WARN, f"Guild with ID {guild.cid} already exists. Refusing to recreate it.")
            return
        
        g = Guild(id=guild.cid)
        session.add(g)
        session.commit()

        session.close()
        return

    def add_channel(self, ch):
        session = new_session()

        if self.check_channel_exists(ch):
            return
        
        c = Channel(id=ch.cid)
        session.add(c)
        session.commit()

        session.close()
        return
    
    def attach_channel(self, ch, guild):
        session = new_session()

        if not self.check_channel_exists(ch):  # Channel must exist
            return

        if not self.check_guild_exists(guild):  # Guild must exist
            return
        
        c = self.get_channel(ch)
        g = self.get_guild(guild)

        session.commit()
        session.close()
        return
    
    def attach_message(self, ch, msg):
        session = new_session()

        if not self.check_channel_exists(ch):  # Channel must exist
            return
        
        c = self.get_channel(ch)
        c.messages.append(msg)

        session.commit()
        session.close()
        return

    def add_message(self, msg):
        session = new_session()

        u = self.get_user(msg.author)
        m = Message(id=msg.cid, content=msg.content, user_id=u)

        session.add(m)

        session.commit()
        session.close()
        return
