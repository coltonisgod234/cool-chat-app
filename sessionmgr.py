import helpers
import csv

def check_if_logged_in(username):
    if get_tok_by_usr(username) != None:
        return True
    else:
        return False

def new_session(token:str, username:str):
    '''
    Writes a new session to sessions.csv
    for the given user
    '''
    with open('sessions.csv', mode="a") as f:
        writer = csv.writer(f)
        writer.writerow([username, token])

def del_session(username:str):
    '''
    removes a session
    '''
    # Remove the session
    try: helpers.csv_remove_line("sessions.csv", get_line_by_usr(username))
    except Exception as e: print("Something error'd but honestly we don't care", e)

def get_tok_by_usr(username:str):
    '''
    Returns the token in sessions.csv where
    a session with the maching username occurs
    '''
    with open('sessions.csv') as f:
        reader = csv.reader(f)

        for line in reader:
            if line[0] == username:
                return line[1]

def new_user(username,password):
    if get_line_by_usr(username) is not None:
        return "That user already exists.", 409
    
    with open("users.csv", mode="a") as f:
        writer = csv.writer(f)
        writer.writerow([username,password])
    
    return "Success", 200

def get_usr_by_tok(token:str):
    '''
    Returns the username in sessions.csv where
    a session with the maching token occurs
    '''
    with open('sessions.csv') as f:
        reader = csv.reader(f)

        for line in reader:
            if line[1] == token:
                return line[0]

def check_login(username:str, password:str):
    '''
    Checks the username and password from users.csv
    '''
    with open('users.csv') as f:
        # Read the data from the CSV file
        reader = csv.reader(f)

        for i,line in enumerate(reader):
            # If our username and passowrd match, then success!
            if line[0] == username and line[1] == password:
                    return True

    return False  # Otherwise, FAILURE!

def get_line_by_usr(username:str, filename="sessions.csv"):
    '''
    Returns the line number in sessions.csv where
    a session with the maching username occurs
    '''
    with open(filename) as f:
        reader = csv.reader(f)

        for i,line in enumerate(reader):
            if line[0] == username:
                return i
    
    return None

def delete_if_logged_in(username:str):
    if check_if_logged_in(username):
        del_session(username)