import utils
import permissions
import dbhelpers

INFO, WARN, ERROR, CRITICAL = utils.get_loglevels()

class User:
    def __init__(self, username:str, password:str, cid=utils.generate_id()):
        utils.log(INFO, f"Creating new user {username}...")
        self.username = username
        self.password = password
        self.token = None
        self.cid = cid
    
    def force_logon(self):
        self.token = utils.generate_id()
    
    def force_logoff(self):
        self.token = None
    
    def token_auth(self, token):
        if self.token == token:
            utils.log(INFO, f"User {self.username} is authenticated")
            return True
        else:
            utils.log(INFO, f"User {self.username} is not authenticated")
            return False
    
    def password_auth(self, password):
        if self.password == password:
            utils.log(INFO, f"User {self.username} is authenticated")
            return True
        else:
            utils.log(INFO, f"User {self.username} is not authenticated")
            return False

    def authenticate(self, password):
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
        del self.messages[cid]
        utils.log(INFO, f"Removed message {cid}")
    
    def edit_message(self, cid, newMsg:Message):
        self.messages[cid] = newMsg
        utils.log(INFO, f"Editted message {cid} to {newMsg.__repr__()}")

    def authorized_add_message(self, msg:Message, token):
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
        self.channels[ch.cid] = ch
        utils.log(INFO, f"Channel {ch.__repr__()} added to guild {self.__repr__()}")
    
    def delete_channel(self, cid):
        del self.channels[cid]
        utils.log(INFO, f"Channel {ch.__repr__()} removed from guild {self.__repr__()}")
