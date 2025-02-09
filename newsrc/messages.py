'''
Manages messaging and core functionality in RAM, this doesn't connect to a database
'''

import utils
import permissions

INFO, WARN, ERROR, CRITICAL, VERBOSE, VERBOSEX = utils.get_loglevels()

class User:
    def __init__(self, username:str, password:str, cid=utils.generate_id()):
        utils.log(INFO, f"Creating new user {username}...")
        self.username = username
        self.password = password
        self.token = None
        self.cid = cid
    
    def force_logon(self):
        '''
        Logs the user in (I.E. Sets their user token) without authentication
        '''
        self.token = utils.generate_id()
    
    def force_logoff(self):
        '''
        Logs the user out
        '''
        self.token = None
    
    def token_auth(self, token):
        '''
        Returns True if the user is authenticated (the given token and the user's token match) or False if not
        '''
        if self.token == token:
            utils.log(VERBOSE, f"User {self.username} is authenticated")
            return True
        else:
            utils.log(VERBOSE, f"User {self.username} is not authenticated")
            return False
    
    def password_auth(self, password):
        '''
        Returns True if the given password and the user's password match, or False if not
        '''
        if self.password == password:
            utils.log(VERBOSE, f"User {self.username} is authenticated")
            return True
        else:
            utils.log(VERBOSE, f"User {self.username} is not authenticated")
            return False

    def authenticate(self, password):
        '''
        Logs the user in given a password
        '''
        if self.password_auth(password):
            self.force_logon()

class Message:
    def __init__(self, author:User, content, timestamp, cid=utils.generate_id()):
        self.author = author
        self.content = content
        self.timestamp = timestamp
        self.cid = cid
    
    def __repr__(self):
        return f'Message(cid={self.cid}), from={self.author}, data={self.content}, at={self.timestamp})'

class Channel:
    def __init__(self, name:str, cid=utils.generate_id()):
        self.cid = cid
        self.messages = {}
        self.permissions = {}
        self.name = name
    
    def __repr__(self):
        return f'Channel(cid={self.cid}, name={self.name}, permissions={self.permissions}, messages={self.messages})'

    def add_message(self, msg:Message):
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
        utils.log(INFO, f"Removed message {cid}")
    
    def edit_message(self, cid, newMsg:Message):
        '''
        Edit a message without authentication
        '''
        self.messages[cid] = newMsg
        utils.log(INFO, f"Editted message {cid} to {newMsg.__repr__()}")

    def authorized_add_message(self, msg:Message, token):
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
    
class Guild:
    def __init__(self, cid=utils.generate_id()):
        self.cid = cid
        self.channels = {}
        self.permissions = {}
    
    def __repr__(self):
        return f'Guild(cid={self.cid}, permissions={self.permissions}, channels={self.channels})'
    
    def add_channel(self, ch:Channel):
        '''
        Attach a given Channel object `ch` to this guild
        '''
        self.channels[ch.cid] = ch
        utils.log(INFO, f"Channel {ch.__repr__()} ({ch.cid}) added to guild {self.__repr__()}")
    
    def delete_channel(self, cid):
        '''
        Detatch the channel with the given CID from this guild
        '''
        del self.channels[cid]
        utils.log(INFO, f"Channel ID {cid} removed from guild {self.__repr__()}")
