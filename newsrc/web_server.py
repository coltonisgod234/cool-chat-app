from flask import Flask, request, make_response

import messages
import utils

app = Flask(__name__)

INFO, WARN, ERROR, CRITICAL, VERBOSE, VERBOSEX = utils.get_loglevels()

users = {
    "colton": messages.User("colton", "abc123")
}
sessions = {}
guilds = {}

def get_session(token):
    return users[ sessions[ token ] ]

@app.route("/api/logon", methods=["POST"])
def login():
    data =   request.json
    uname =  data["username"]
    passwd = data["password"]

    users[uname].authenticate(passwd)
    token = users[uname].token
    if token is None:
        return "No", 404

    r = make_response(token)
    r.set_cookie("token", token, secure=True, samesite="None")
    sessions[token] = uname
    utils.log(INFO, f"login: usr={uname}, pass={passwd}, tok={token}")
    return r

@app.route("/api/newuser", methods=["POST"])
def newuser():
    data =   request.json
    uname =  data["username"]
    passwd = data["password"]
    users[uname] = messages.User(uname, passwd)

    utils.log(INFO, f"new user: {uname}")

    return "OK"

@app.route("/api/newguild", methods=["POST"])
def newguild():
    data = request.json
    token = data["token"]

    cid = utils.generate_id()
    guilds[cid] = messages.Guild(cid)

    utils.log(INFO, f"newguild: req={data}, cid={cid}, out={guilds[cid]}")

    return cid

@app.route("/api/newchannel", methods=["POST"])
def addchannel():
    data =  request.json
    token = data["token"]
    guild = data["guildid"]
    name =  data["name"]

    cid = utils.generate_id()
    guilds[guild].channels[cid] = messages.Channel(name, cid)

    utils.log(INFO, f"newchannel: req={data}.tok={token}.guild={guild}\
        .name={name}, cid={cid}, out={guilds[guild].channels[cid]}")

    return cid

@app.route("/api/sendmsg", methods=["POST"])
def addmsg():
    data = request.json
    token = data["token"]
    channel = data["channel"]
    guild = data["guild"]
    content = data["content"]

    uname = get_session(token)
    message = messages.Message(uname, content, "")

    guilds[guild].channels[channel].add_message(message)
    return message.cid

app.run()