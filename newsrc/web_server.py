from flask import Flask, request, make_response

import messages
import permissions
import utils

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

    if users.get(username) is not None:
        return "Already exists", 409

    user = messages.User(username, password)
    users[username] = user
    return "OK", 200

@app.route("/api/users/delete", methods=["POST"])
def usrdel():
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)

    if users.get(username) is not None:
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

@app.route("/api/guilds/channels", methods=["POST"])
def guild_chlist():
    token = utils.get_request_token(request)
    username = utils.get_username_by_token(token, users)
    if token == None or username == None:
        return "Nope!", 401

app.run()