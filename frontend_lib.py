import sessionmgr
import messaging
import csv
from flask import render_template
import os

def show_messages(guild, channel, token):
    # Define the file path
    file_path = f"data/{guild}/{channel}.csv"

    # Check if the file exists
    if not os.path.exists(file_path):
        return f"HTTP status 404.", 404

    # Read messages from the file
    messages = []
    with open(file_path, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                messages.append({"username": row[0], "content": row[1]})

    return render_template('messages.html', guild=guild, channel=channel, messages=messages)
