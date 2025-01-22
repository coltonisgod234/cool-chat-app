import helpers
import sessionmgr
import csv

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

    return {
        "raw": perms,
        "user": username,
        "guild": guild,
        "channel": channel,
        "metatype": metatype,
        "send_message": perms[1],
        "owner": perms[2]
    }

def new_guild(ID, token):
    path = f"data/{ID}"
    if os.exists(path):
        return "A guild with that ID already exists", 422
    
    user = sessionmgr.get_usr_by_tok(token)
    if not sessionmgr.check_if_logged_in(user):
        return "Invalid token", 401

    os.mkdir(path)

    # Register the user as owner
    with open(f"{path}/__GUILD.meta.perms", mode="a") as f:
        writer = csv.writer(f)
        writer.writerow([user,"yes","yes"])

def new_channel(guild, channel, token):
    path = f"data/{guild}/{channel}"
    if os.exists(path):
        return "That channel already exists", 422
    
    user = sessionmgr.get_usr_by_tok(token)
    if not sessionmgr.check_if_logged_in(user):
        return "Invalid token", 401

    open(f"{path}.csv", mode="x")  # Create file
    with open(f"{path}.meta.members.perms", mode="a") as f:
        writer = csv.writer(f)
        writer.writerow([user,"yes","yes"])
    
    return f"Created channel {guild}/{channel}.", 200
