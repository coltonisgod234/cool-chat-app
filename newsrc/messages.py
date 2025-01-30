import uuid
import csv

def generate_id():
    return str(uuid.uuid4())

def edit_permission(obj, key, entry):
    obj.permissions[key] = entry
    return obj

def grant_permission(obj, key, permission):
    o = obj.permissions[key]
    o.__setattr__(permission, True)

    obj.permissions[key] = o
    return obj

def revoke_permission(obj, key, permission):
    o = obj.permissions[key]
    o.__setattr__(permission, False)

    obj.permissions[key] = o
    return obj

def check_permission(obj, key, permission):
    try:
        return obj.permissions[key].__getattribute__(permission)
    except KeyError:
        return None

class User:
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
        self.token = None
    
    def force_logon(self):
        self.token = generate_id()
    
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
    def __init__(self, author:User, content, timestamp, cid=generate_id()):
        self.author = author
        self.content = content
        self.timestamp = timestamp
        self.cid = cid
    
    def __repr__(self):
        return f'Message(cid={self.cid}), from={self.author}, data={self.content}, at={self.timestamp})'

class Channel:
    def __init__(self, name:str, cid=generate_id()):
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
        if not check_permission(self, username, "send_messages"):
            raise PermissionError("You do not have the required permission 'send_messages'")
        
        return self.force_add_message(msg)
    
class Guild:
    def __init__(self, cid=generate_id()):
        self.cid = cid
        self.channels = {}
        self.permissions = {}
    
    def __repr__(self):
        return f'Guild(cid={self.cid}, permissions={self.permissions}, channels={self.channels})'
    
    def add_channel(self, ch:Channel):
        self.channels[ch.cid] = ch

class GuildPermissionEntry:
    def __init__(self, raw:str, user:User, guild:Guild,
                create_channel:bool, delete_channel:bool, manage_channel:bool,
                view_perms:bool, manage_perms:bool,
    ):
        self.raw = raw
        self.user = username
        self.guild = guild
        self.create_channel = create_channel
        self.delete_channel = delete_channel
        self.manage_channel = manage_channel
        self.view_perms = view_perms
        self.manage_perms = manage_perms

class ChannelPermissionEntry:
    def __init__(
        self, raw:str, user:User, channel:Channel,
        send_messages:bool, delete_messages:bool, manage_messages:bool
    ):
        self.raw = raw
        self.user = user
        self.channel = channel
        self.send_messages = send_messages
        self.delete_channel = delete_messages
        self.manage_messages = manage_messages

u = User("colton", "abc123")
u.authenticate("abc123")

g = Guild()
c = Channel("general")
c = edit_permission(c, u.username, ChannelPermissionEntry("", u, c, False, False, False))
c = grant_permission(c, u.username, "send_messages")

g.add_channel(c)

msg = Message(u, "Hey!", "")
g.channels[c.cid].add_message(msg, u.token)

print(g)