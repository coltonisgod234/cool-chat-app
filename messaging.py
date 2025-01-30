import helpers
import sessionmgr
import csv

class Guild:
    def __init__(self):
        self.channels = []

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

    def check_perm(self, token, permission):
        # Check 2: Make sure the user is authorized
        username = sessionmgr.get_usr_by_tok(token)
        if not sessionmgr.check_if_logged_in(username):
            return PermissionError("You aren't authenticated")

        return getattr(self, permission, None)

class ChannelPermissionEntry:
    def __init__(self,
        raw:str, user:str, guild:str, channel:str,
        send_messages:bool
    ):
        self.raw = raw
        self.user = user
        self.guild = guild
        self.channel = channel
        self.send_messages = send_messages
    
    def check_perm(self, token, permission):
        # Check 2: Make sure the user is authorized
        username = sessionmgr.get_usr_by_tok(token)
        if not sessionmgr.check_if_logged_in(username):
            return PermissionError("You aren't authenticated")

        return getattr(self, permission, None)

def send_msg(token, content, guild, channel):
    '''
    Sends a message
    '''
    username = sessionmgr.get_usr_by_tok(token)
    if not check_perm(token, guild, channel, "send_message"):
        return "No permission", 401

    with open(f"data/{guild}/{channel}.csv", mode="a") as f:
        writer = csv.writer(f)
        writer.writerow([username,content])  # FORMAT: sender,content
    
    return "Message Sent!", 200

def check_perm(token, guild, channel, perms):
    sender_name = sessionmgr.get_usr_by_tok(token)
    if sender_name is None:  # If no such token exists, that person isn't logged in
        return ("Bad or expired token", 401)

    p = get_ch_perms(guild, channel, "members.perms", sender_name)
    if p[perms] == "no":
        # Make sure that the user is actually allowed to do that
        return False
    else:
        return True

def get_ch_perms(guild, channel, metatype, username:str):
    '''
    Formats a permissions dict
    '''
    print(guild, channel)
    path = f"data/{guild}/{channel}.meta.{metatype}"
    perms = helpers.search_for_data(username, 0, path)  # FORMAT: user, perm_send_msg

    # Check if the user has an entry
    if perms == None:
        return None

    return GuildPermissionEntry(
        perms,
        username,
        guild,
        perms[1],
        perms[2],
        perms[3],
        perms[4],
        perms[5]
    )

def new_guild(ID, token):
    path = f"data/{ID}"
    if os.path.exists(path):
        return "A guild with that ID already exists", 422
    
    user = sessionmgr.get_usr_by_tok(token)
    if not sessionmgr.check_if_logged_in(user):
        return "Invalid token", 401

    # Create the guild
    os.mkdir(path)

    # Register the user as owner
    with open(f"{path}/gmeta.perms", mode="a") as f:
        writer = csv.writer(f)
        writer.writerow([user,"yes","yes","yes","yes"]) # First permission is "owner"

def new_channel(guild, channel, token):
    # Check 1: Ensure the channel doesn't already exist
    path = f"data/{guild}/{channel}.csv"
    if os.path.exists(path):
        return "That channel already exists", 422
    
    # Check 2: Ensure the user is authenticated
    user = sessionmgr.get_usr_by_tok(token)  # Convert the token into a username for check_if_logged_in()
    if not sessionmgr.check_if_logged_in(user):
        # If the user is not logged in, stop them from continuing.
        return "Invalid token", 401

    # Check 3: Ensure the user is allowed to create channels
    gperms = get_guild_perms(guild, token)

    # Create the channel
    open(f"{path}.csv", mode="x")  # Create file
    with open(f"{path}.meta.members.perms", mode="a") as f:
        writer = csv.writer(f)
        writer.writerow([user,"yes","yes"])
    
    return f"Created channel {guild}/{channel}.", 200
