from flask import Flask, request, make_response

import messages
import utils

app = Flask(__name__)

users = {
    "colton": messages.User("colton", "abc123")
}
guilds = {}

@app.route("/api/logon", methods=["POST"])
def login():
    data = request.json
    uname = data["username"]
    passwd = data["password"]

    users[uname].authenticate(passwd)
    if users[uname].token is None:
        return "No", 404

    r = make_response(users[uname].token)
    r.set_cookie("token", users[uname].token, secure=True, samesite="None")
    return r

@app.route("/api/newuser", methods=["POST"])
def newuser():
    data = request.json
    uname = data["username"]
    passwd = data["password"]
    users[uname] = messages.User(uname, passwd)

    return "OK"

@app.route("/api/newguild", methods=["POST"])
def newguild():
    data = request.json
    token = data["token"]

    cid = utils.generate_id()
    guilds[cid] = messages.Guild(cid)

    return cid

@app.route("/api/newchannel", methods=["POST"])
def addchannel():
    data = request.json
    token = data["token"]
    guild = data["guildid"]
    name = data["name"]

    cid = utils.generate_id()
    guilds[guild].channels[cid] = messages.Channel(name, cid)

    return cid

app.run()