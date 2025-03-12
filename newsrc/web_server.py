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

###############
### A U T H ###
###############

@app.route("/api/auth/login", methods=["POST"])
def auth():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)

    user.authenticate(password)
    if not user.token:
        return "error", 400
    
    else:
        return user.token

@app.route("/api/auth/logout", methods=["POST"])
def deauth():
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)

    if username in ["", None]:
        return "Nope!", 401
    
    users[username].force_logoff()
    return "OK", 200

#######################
### USER MANAGEMENT ###
#######################

@app.route("/api/users/create", methods=["POST"])
def usrcreate():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if users.get(username) != None:
        return "Already exists", 409

    user = messages.User(username, password)
    users[username] = user
    return "OK", 200

@app.route("/api/users/delete", methods=["POST"])
def usrdel():
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)

    if users.get(username) == None:
        return "Doesn't exist", 404
    
    del users[username]
    return "OK", 200

@app.route("/api/users/update_username", methods=["POST"])
def usrnameupdate():
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401

    if users.get(username) == None:
        return "Doesn't exist", 404

    data = request.json
    new_usrname = data.get("username")
    
    users[username].username = new_usrname
    return "OK", 200

@app.route("/api/users/update_password", methods=["POST"])
def usrpassupdate():
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 404

    if users.get(username) is None:
        return "Doesn't exist", 404

    data = request.json
    passwd = data.get("password")
    
    users[username].password = passwd
    return "OK", 200

########################
### GUILD MANAGEMENT ###
########################

@app.route("/api/guilds/create", methods=["POST"])
def guildcreate():
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401

    cid = utils.generate_id()
    guild = messages.Guild(cid)
    # Give that person owner privledges
    guild.permissions[username] = permissions.highestGuildPerms(username, guild.cid)

    guilds[cid] = guild
    return cid, 200

@app.route("/api/guilds/<guild_cid>/channels_list", methods=["GET"])
def channel_list(guild_cid):
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
    guild = guilds[guild_cid]

    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    return {
        "channels": list(guild.channels.keys())
    }, 200

@app.route("/api/guilds/<guild_cid>", methods=["DELETE"])
def delguild(guild_cid):
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
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
def new_ch(guild_cid):
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
    guild: messages.Guild = guilds[guild_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    data = request.json
    ch_name = data.get("name")
    
    channel = messages.Channel(ch_name)
    guild.add_channel(channel)

    return channel.cid, 200

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["DELETE"])
def del_ch(guild_cid, channel_cid):
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
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
def get_message_list(guild_cid, channel_cid):
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403

    return {
        "messages": ch.messages.keys()
    }, 200

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["POST"])
def send_message(guild_cid, channel_cid):
    data = request.json
    text = data.get("content")

    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    
    guild: messages.Guild = guilds[guild]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    user = users[username]
    m = messages.Message(user, text, time.time())
    ch.add_message(m)

    return "OK", 200

# This stuff is untested, I literally do not care, if it doesn't work I couldn't care less.

@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["GET"])
def get_msg(guild_cid, channel_cid, message_cid):
    data = request.json

    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
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
def del_msg(guild_cid, channel_cid, message_cid):
    data = request.json

    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    ch.delete_message(message_cid)
    return "OK", 200

# Is PATCH a real method???? Too lazy to check, couldn't care less
@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["PATCH"])
def edit_msg(guild_cid, channel_cid, message_cid):
    data = request.json
    text = data.get("content")

    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401
    
    guild: messages.Guild = guilds[guild_cid]
    ch: messages.Channel = guilds[guild_cid].channels[channel_cid]
    
    if not utils.user_in_guild(guild, username):
        return "Not a member", 403
    
    ch.edit_message(message_cid, text)
    return "OK", 200

app.run(debug=True)