from flask import Flask, request, abort, make_response, render_template, Response, send_file, send_from_directory, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import csv
import os
import string
import time

import sessionmgr as sessions
import helpers
import messaging
import frontend_lib as front

app = Flask(__name__)
app.app_context().push()
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

pfps = front.get_all_pfp()

server_ip = "https://coltons.sytes.net"
new_messages = []

@app.route('/')
def index():
    try:
        token = request.cookies["token"]
        username = sessions.get_usr_by_tok(token)
    except:
        return render_template("quicklinks.html",
            header="Quick Links",
            message="",
            server_ip="https://coltons.sytes.net",
            currentuser="Literally Nobody"
        )
    
    return render_template("quicklinks.html",
        header="Quick Links",
        message="",
        server_ip="https://coltons.sytes.net",
        currentuser=username
    )

@app.route('/api/login', methods=["POST"])
@limiter.limit("30 per second")
def login():
    # Get the query parameters from the URL
    data = request.json
    username = data.get('username', None)
    password = data.get('password', None)

    token = helpers.make_UUID(96)

    if sessions.check_login(username, password):
        sessions.delete_if_logged_in(username)
        sessions.new_session(token, username)
        
        responce = make_response(token)
        responce.set_cookie("token", token, secure=True, samesite="None")
        return responce
    else:
        return "Incorrect Credentials", 401

@app.route('/api/refresh_pfp')
@limiter.limit("40 per minute")
def refresh_pfps():
    global pfps

    pfps = front.get_all_pfp()
    return "OK", 200

@app.route('/login_fe')
def login_fe():
    return render_template("login.html")

@app.route('/api/logout', methods=["POST"])
def logout():
    data = request.json
    token = data.get('token', request.cookies["token"])

    username = sessions.get_usr_by_tok(token)
    if username is None:
        return f"No such user", 404

    sessions.del_session(username)

    responce = make_response(f"Logged Out {username} ({token})")
    responce.delete_cookie("token")
    return responce

@app.route("/channel_sel")
def channel_sel_idx():
    return render_template("channelselector.html")

@app.route('/logout_fe')
def logout_inpl():
    try: token = request.cookies["token"]
    except: return f"You aren't logged in.", 404

    username = sessions.get_usr_by_tok(token)
    if username is None:
        return "No such user", 404

    sessions.del_session(username)

    responce = make_response(f"Logged Out {username} ({token})<br><a href='{server_ip}/login_fe'>Log in</a>")
    responce.delete_cookie("token")
    return responce

@app.route('/api/message', methods=["POST"])
@limiter.limit("4 per second")
def send():
    global new_messages
    global pfps

    data = request.json
    token = data.get("token")
    guild = data.get("guildID")
    channel = data.get("channelID")
    content = data.get("content")


    username = sessions.get_usr_by_tok(token)

    if not sessions.check_if_logged_in(username):
        return "Invalid token", 401

    code = messaging.send_msg(token, content, guild, channel)

    new_messages.append({
        "guild": guild,
        "channel": channel,
        "content": content,
        "username": username,
        "pfp": pfps[username]
    })
    print("CURRENT NEW MESSAGES", new_messages)

    if not code:
        return "OK", 200
    else:
        return code

@app.route("/api/set_pfp", methods=["POST"])
@limiter.limit("1 per second")
def update_pfp():
    token = request.form.get("token")
    pfp = request.files["pfp"]
    print(pfp)

    return sessions.update_pfp_backend(token, pfp)

@app.route("/update_pfp")
def update_pfp_page():
    return render_template("changepfp.html")

@app.route("/uploads/<path:filename>")
def get_pfp_frontend(filename):
    path = f"uploads/{filename}"
    print("PFP PATH", path)
    return send_file(path)

@app.route("/api/see_messages", methods=["POST"])
def view():
    data = request.json
    token = data.get("token")
    guild = data.get("guildID")
    channel = data.get("channelID")

    return front.show_messages(guild, channel, token, pfps)

@app.route("/api/new_user", methods=["POST"])
@limiter.limit("15 per minute")
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    return sessions.new_user(username, password)

@app.route("/signup")
def sign_up():
    return render_template("signup.html")

@app.route("/frontend_view_channel", methods=["GET"])
def view_fe():
    try: token = request.cookies["token"]
    except: return "Bad token cookie", 401

    username = sessions.get_usr_by_tok(token)

    if not sessions.check_if_logged_in(username):
        return "No session", 401
    
    guild = request.args.get("g")
    channel = request.args.get("c")
    print(channel, guild)

    return front.show_messages(guild, channel, token, pfps)
    #return front.show_messages(guild=guild, channel=channel, token=token)

@app.route('/messages/<guild>/<channel>')
def give_messages(guild, channel):
    try:
        token = request.cookies["token"]
        username = sessions.get_usr_by_tok(token)
    except:
        return "Bad cookie", 401
    
    if not sessions.check_if_logged_in(username):
        return "Bad token", 401
    
    can_view = messaging.check_perm(token, guild, channel, "view_channel")
    if can_view is None or can_view == False:
        return "No permission", 401
    
    path = f"data/{guild}/{channel}.csv"

    #if os.path.exists(path):
    #    return "No such channel", 404
    
    with open(path) as f:
        data = f.read()
    
    return data, 200

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('ssl/selfsigned.cer', 'ssl/selfsigned.key'), port=5000, host="0.0.0.0", threaded=True)
    #app.run(debug=True, port=443, host='0.0.0.0', threaded=True)
