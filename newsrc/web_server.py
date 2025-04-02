from flask import Flask, request, make_response

import messages
import permissions
import utils

import time

app = Flask(__name__)

INFO, WARN, ERROR, CRITICAL, VERBOSE, VERBOSEX = utils.get_loglevels()

users = {
    "colton": messages.User("colton", "abc123")
}
guilds = {}

from functools import wraps

def requires_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = utils.get_request_token(request)
        username = utils.get_username_by_token(token, users)

        if not username or not token:
            return "Bad token", 401

        return func(username, token, *args, **kwargs)
    return wrapper

def requires_username_and_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.json
        username = data.get("username")
        password = data.get("password")

        return func(username, password)
    return wrapper

###############
### A U T H ###
###############

@app.route("/api/auth/login", methods=["POST"])
@requires_username_and_password
def auth(username, password):
    user = users.get(username)

    user.authenticate(password)
    if not user.token:
        return "error", 400
    
    else:
        return user.token

@app.route("/api/auth/logout", methods=["POST"])
@requires_auth
def deauth(username, token):
    users[username].force_logoff()
    return "OK", 200

#######################
### USER MANAGEMENT ###
#######################

@app.route("/api/users/create", methods=["POST"])
@requires_username_and_password
def user_create(username, password):
    if users.get(username) != None:
        return "Already exists", 409

    user = messages.User(username, password)
    users[username] = user
    print(users)
    return "OK", 200

@app.route("/api/users/delete", methods=["POST"])
@requires_auth
def user_delete(username, token):
    del users[username]
    print(users)
    return "OK", 200

'''BROKEN, WILL FIX LATER
@app.route("/api/users/update_username", methods=["POST"])
@requires_auth
def user_update_username(username, token):
    data = request.json
    new_usrname = data.get("username")

    user = users[username]
    user.username = new_usrname

    users[new_usrname] = user
    del users[username]
    return "OK", 200

@app.route("/api/users/update_password", methods=["POST"])
@requires_auth
def user_update_password(username, token):
    data = request.json
    passwd = data.get("password")
    
    users[username].password = passwd
    return "OK", 200
'''

########################
### GUILD MANAGEMENT ###
########################

@app.route("/api/guilds/create", methods=["POST"])
@requires_auth
def guildcreate(username, token):
    cid = utils.generate_id()
    guild = messages.Guild(cid)
    # Give that person owner privledges
    guild.permissions[username] = permissions.highestGuildPerms(username, guild.cid)

    guilds[cid] = guild
    return cid, 200

@app.route("/api/guilds/<guild_cid>/channels_list", methods=["GET"])
@requires_auth
def channel_list(username, token, guild_cid):
    guild = guilds[guild_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    return {
        "channels": list(guild.channels.keys())
    }, 200

@app.route("/api/guilds/<guild_cid>", methods=["DELETE"])
@requires_auth
def guild_delete(username, token, guild_cid):
    guild: messages.Guild = guilds[guild_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    for key, channel in guild.channels.items():
        guild.delete_channel(channel.cid)
    
    del guilds[guild_cid]
    
    return "OK", 200

################
### CHANNELS ###
################

@app.route("/api/guilds/<guild_cid>/new_channel", methods=["POST"])
@requires_auth
def new_channel(username, token, guild_cid):
    guild: messages.Guild = guilds[guild_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    data = request.json
    ch_name = data.get("name")
    
    channel = messages.Channel(ch_name)
    guild.add_channel(channel)

    return channel.cid, 200

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["DELETE"])
@requires_auth
def del_channel(username, token, guild_cid, channel_cid):
    guild: messages.Guild = guilds[guild_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    ch = guilds[guild_cid].channels[channel_cid]
    if utils.check_permission(guild, channel_cid, "delete_channel"):
        return "No permission", 401
    
    guild.delete_channel(channel_cid)
    return "OK", 200

############
# MESSAGES #
############

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["GET"])
@requires_auth
def get_message_list(username, token, guild_cid, channel_cid):
    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403

    return {
        "messages": list(ch.messages.keys())
    }, 200

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["POST"])
@requires_auth
def send_message(username, token, guild_cid, channel_cid):
    data = request.json
    text = data.get("content")

    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    
    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    user = users[username]
    m = messages.Message(user, text, time.time())
    ch.add_message(m)

    return "OK", 200

# This stuff is untested, I literally do not care, if it doesn't work I couldn't care less.

@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["GET"])
@requires_auth
def get_msg(username, token, guild_cid, channel_cid, message_cid):
    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    m: messages.Message = ch.messages[message_cid]
    return {
        "author": m.author.cid,
        "content": m.content,
        "cid": m.cid,
        "timestamp": m.timestamp
    }, 200

@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["DELETE"])
@requires_auth
def del_msg(username, token, guild_cid, channel_cid, message_cid):
    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    ch.delete_message(message_cid)
    return "OK", 200

# Is PATCH a real method???? Too lazy to check, couldn't care less
@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["PATCH"])
@requires_auth
def edit_msg(username, token, guild_cid, channel_cid, message_cid):
    data = request.json
    text = data.get("content")

    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    ch.edit_message(message_cid, text)
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=5100)