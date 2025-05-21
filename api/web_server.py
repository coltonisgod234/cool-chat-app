from flask import Flask, request, make_response, jsonify
from functools import wraps
import time

from data.database import Database
from data.repositories import UserRepository, GuildRepository, ChannelRepository, MessageRepository
from service.auth_service import AuthService
from service.chat_service import ChatService
from service import utils

# Initialize app
app = Flask(__name__)

# Initialize database
db = Database()
db.create_tables()

# Initialize repositories
user_repo = UserRepository(db)
guild_repo = GuildRepository(db)
channel_repo = ChannelRepository(db)
message_repo = MessageRepository(db)

# Initialize services
auth_service = AuthService(user_repo)
chat_service = ChatService(message_repo, channel_repo, guild_repo, user_repo)

# Initialize default user
auth_service.initialize_users()

# Logging
INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG = utils.get_loglevels()

# Authentication decorators
def requires_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = utils.get_request_token(request)
        username = auth_service.get_username_by_token(token)

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
    token = auth_service.login(username, password)
    if not token:
        return "error", 400
    
    return token

@app.route("/api/auth/logout", methods=["POST"])
@requires_auth
def deauth(username, token):
    auth_service.logout(username)
    return "OK", 200

#######################
### USER MANAGEMENT ###
#######################

@app.route("/api/users/create", methods=["POST"])
@requires_username_and_password
def user_create(username, password):
    if not auth_service.create_user(username, password):
        return "Already exists", 409

    return "OK", 200

@app.route("/api/users/delete", methods=["POST"])
@requires_auth
def user_delete(username, token):
    auth_service.delete_user(username)
    return "OK", 200

########################
### GUILD MANAGEMENT ###
########################

@app.route("/api/guilds/create", methods=["POST"])
@requires_auth
def guildcreate(username, token):
    try:
        guild_cid = chat_service.create_guild(username)
        return guild_cid, 200
    except (ValueError, PermissionError) as e:
        return str(e), 400

@app.route("/api/guilds/<guild_cid>/channels_list", methods=["GET"])
@requires_auth
def channel_list(username, token, guild_cid):
    try:
        channels = chat_service.get_channels_in_guild(guild_cid, username)
        return {"channels": channels}, 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

@app.route("/api/guilds/<guild_cid>", methods=["DELETE"])
@requires_auth
def guild_delete(username, token, guild_cid):
    try:
        chat_service.delete_guild(guild_cid, username)
        return "OK", 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

################
### CHANNELS ###
################

@app.route("/api/guilds/<guild_cid>/new_channel", methods=["POST"])
@requires_auth
def new_channel(username, token, guild_cid):
    try:
        data = request.json
        channel_name = data.get("name")
        
        channel_cid = chat_service.create_channel(guild_cid, channel_name, username)
        return channel_cid, 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["DELETE"])
@requires_auth
def del_channel(username, token, guild_cid, channel_cid):
    try:
        chat_service.delete_channel(guild_cid, channel_cid, username)
        return "OK", 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

############
# MESSAGES #
############

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["GET"])
@requires_auth
def get_message_list(username, token, guild_cid, channel_cid):
    try:
        messages = chat_service.get_messages(guild_cid, channel_cid, username)
        return {"messages": messages}, 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

@app.route("/api/guilds/<guild_cid>/<channel_cid>", methods=["POST"])
@requires_auth
def send_message(username, token, guild_cid, channel_cid):
    try:
        data = request.json
        content = data.get("content")
        
        message_cid = chat_service.send_message(guild_cid, channel_cid, username, content)
        return "OK", 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["GET"])
@requires_auth
def get_msg(username, token, guild_cid, channel_cid, message_cid):
    try:
        # In a real implementation, we'd use a repository to get the message details
        # For now, we'll just say it's not implemented
        return "Not implemented", 501
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["DELETE"])
@requires_auth
def del_msg(username, token, guild_cid, channel_cid, message_cid):
    try:
        chat_service.delete_message(guild_cid, channel_cid, message_cid, username)
        return "OK", 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

@app.route("/api/guilds/<guild_cid>/<channel_cid>/<message_cid>", methods=["PATCH"])
@requires_auth
def edit_msg(username, token, guild_cid, channel_cid, message_cid):
    try:
        data = request.json
        content = data.get("content")
        
        chat_service.edit_message(guild_cid, channel_cid, message_cid, username, content)
        return "OK", 200
    except ValueError as e:
        return str(e), 404
    except PermissionError as e:
        return str(e), 403

if __name__ == "__main__":
    app.run(debug=True, port=5100) 