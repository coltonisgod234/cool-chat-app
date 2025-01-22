import sessionmgr
import messaging
import csv
from flask import render_template
import os
import helpers

def get_all_pfp():
    pfp_dict = {}
    with open("users.csv") as f:
        reader = csv.reader(f)
        for line in reader:
            user = line[0]
            pfp = line[2]

            pfp_dict[user] = pfp
    
    return pfp_dict

def show_messages(guild, channel, token, pfps):
    # Define the file path
    file_path = f"data/{guild}/{channel}.csv"

    username = sessionmgr.get_usr_by_tok(token)

    # Check if the file exists
    if not os.path.exists(file_path):
        return render_template("quicklinks.html",
            header="404 Not Found",
            message="",
            server_ip="https://coltons.sytes.net",
            currentuser=username
        )

    # Read messages from the file
    messages = []
    with open(file_path, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                messages.append({"username": row[0], "content": row[1], "pfp": pfps[row[0]]})

    return render_template('messages.html', guild=guild, channel=channel, messages=messages, currentuser=username)
