from flask import Flask, request, abort, make_response, render_template, Response
import csv
import os
import string

import sessionmgr as sessions
import helpers
import messaging
import frontend_lib as front

app = Flask(__name__)

server_ip = "https://coltons.sytes.net"
new_messages = False

@app.route('/')
def index():
    return f"""
    Please <a href='{server_ip}/login_fe'>log in</a> to continue
    """

@app.route('/login', methods=["POST"])
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
        responce.set_cookie("token", token, secure=True)
        return responce
    else:
        return "Incorrect Credentials", 401

@app.route('/login_fe')
def login_fe():
    return render_template("login.html")

@app.route('/logout', methods=["POST"])
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

@app.route('/logout_fe')
def logout_inpl():
    try: token = request.cookies["token"]
    except: return f"You aren't logged in.<br><a href='{server_ip}/login_fe'>Log in</a>", 404

    username = sessions.get_usr_by_tok(token)
    if username is None:
        return "No such user", 404

    sessions.del_session(username)

    responce = make_response(f"Logged Out {username} ({token})<br><a href='{server_ip}/login_fe'>Log in</a>")
    responce.delete_cookie("token")
    return responce

@app.route('/message', methods=["POST"])
def send():
    global new_messages

    data = request.json
    token = data.get("token")
    guild = data.get("guildID")
    channel = data.get("channelID")
    content = data.get("content")

    if not sessions.check_if_logged_in(sessions.get_usr_by_tok(token)):
        return "Invalid token", 401

    code = messaging.send_msg(token, content, guild, channel)  # 127.0.0.1:5000/message?g=1&c=general&m=hello&t=PAazos7mIDJGhG68nabOIp7dLKTI7degGk70NC7de2AUizqCkgDlLOCfpgeYLyIdRN6kHr4O2H9HPhaZpf8Df2PhcKKsw17t
    new_messages = True
    return code

@app.route("/see_messages", methods=["POST"])
def view():
    data = request.json
    token = data.get("token")
    guild = data.get("guildID")
    channel = data.get("channelID")

    return front.show_messages(guild, channel)

@app.route("/new_user", methods=["POST"])
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
    except: return f"You are not logged in\n<a href='{server_ip}/login_fe'>Log In</a>", 401
    
    guild = request.args.get("g")
    channel = request.args.get("c")
    print(channel, guild)

    return front.show_messages(guild=1, channel="general", token=request.cookies["token"])
    #return front.show_messages(guild=guild, channel=channel, token=token)

@app.route('/events')
def sse():
    def generate():
        global new_messages
        while True:
            if new_messages == True: 
                yield "data: {\"action\": \"refresh\"}\n\n"
                new_messages = False
                print("CLIENTS SHOULD REFRESH")

    return Response(generate(), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('ssl/server.crt', 'ssl/server.key'), port=443, host='0.0.0.0')
