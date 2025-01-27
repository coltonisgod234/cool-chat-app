import uuid

class User:
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
        self.token = None
    
    def force_logon(self):
        self.token = str(uuid.uuid4())
    
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
    
    def token_unauth(self, token):
        '''
        Checks if a token is NOT authenticated
        '''
        return not self.token_auth(token)

class GuildPermissionEntry:
    def __init__(self, raw:str, user:str, guild:str,
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

    def check_perm(self, user:User, token, permission):
        # Gather needed info
        username = user.username
        # Check 2: Make sure the user is authorized
        if user.token_unauth(token): return PermissionError("You aren't authenticated")

        return getattr(self, permission, None)

class Message:
    def __init__(self, author, content, timestamp, id:int):
        self.author = author
        self.content = content
        self.timestamp = timestamp
        self.uid = id

class Channel:
    def __init__(self, id:int, name:str, guild_id:int):
        self.gid = guild_id
        self.uid = id
        self.messages = []
        self.name = name

    def add_message(self, msg:Message) -> Message:
        self.messages.append(msg)
        return msg

class Guild:
    def __init__(self, id):
        self.uid = id
        self.channels = []
        self.permissions = {}
    
    def add_channel(self, ch:Channel):
        self.channels.append(ch)
    
    def check_perm(self, user, perm):
        try:                p = self.permissions[user].__getattr__(perm)
        except KeyError:    return None
        finally:            return p

    def edit_permission(self, user:User, token, entry:GuildPermissionEntry):
        if user.token_unauth(token): return PermissionError("You aren't authenticated")
        if check_perm(user, )

        self.permissions[user] = entry

g = Guild(0)
c = Channel(0, "general", g.uid)

u = User("colton", "abc123")
u.authenticate("abc123")

g.add_channel(c)

print(g.channels)

msg = Message(u, "Hey!", "", str(uuid.uuid4()))
g.channels[0].add_message(msg)

print(g.channels[0].messages[0])