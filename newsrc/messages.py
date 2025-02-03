import utils
import permissions
import database

DATABASE_PATH = "db/"

class User:
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
        self.token = None
    
    def force_logon(self):
        self.token = utils.generate_id()
    
    def force_logoff(self):
        self.token = None
    
    def token_auth(self, token):
        if self.token == token:
            return True
        else:
            return False
    
    def password_auth(self, password):
        if self.password == password:
            return True
        else:
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

    def force_add_message(self, msg:Message):
        '''
        Add message without authentication
        '''
        self.messages[msg.cid] = msg
        return msg
    
    def force_delete_message(self, cid):
        del self.messages[cid]
    
    def force_edit_message(self, cid, newMsg:Message):
        self.messages[cid] = newMsg

    def add_message(self, msg:Message, token):
        username = msg.author.username

        # Ensure the user is authenticated
        if not msg.author.token_auth(token):
            raise PermissionError("Bad token")

        # Ensure they have permission
        if not utils.check_permission(self, username, "send_messages"):
            raise PermissionError("You do not have the required permission 'send_messages'")
        
        return self.force_add_message(msg)
    
class Guild:
    def __init__(self, cid=utils.generate_id()):
        self.cid = cid
        self.channels = {}
        self.permissions = {}
    
    def __repr__(self):
        return f'Guild(cid={self.cid}, permissions={self.permissions}, channels={self.channels})'
    
    def force_add_channel(self, ch:Channel):
        self.channels[ch.cid] = ch
    
    def force_delete_channel(self, cid):
        del self.channels[cid]

u = User("colton", "abc123")
u.authenticate("abc123")

g = Guild()
c = Channel("general")
c = utils.edit_permission(c, u.username, permissions.ChannelPermissionEntry("", u, c, False, False, False))
c = utils.grant_permission(c, u.username, "send_messages")

g.force_add_channel(c)

msg = Message(u, "Hey!", "")
g.channels[c.cid].add_message(msg, u.token)

print(g)

db = database.DatabaseFile("test.csv")
db.connect('w')
db.write('nice', 'cool', False)