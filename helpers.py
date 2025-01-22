import csv
import os
import string

def csv_remove_line(filename:os.PathLike, line:int):
    # Read the CSV file and filter out the line to remove
    with open(filename, 'r') as infile:
        reader = csv.reader(infile)
        rows = [row for i, row in enumerate(reader) if i != line]

    # Write the remaining rows back to the CSV file
    with open(filename, 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)

def make_UUID(length):
    # Generate random bytes
    random_bytes = os.urandom(length)
    
    # Define the printable characters
    printable_characters = string.ascii_letters + string.digits

    # Convert random bytes to a string with printable characters
    result = ''.join(printable_characters[b % len(printable_characters)] for b in random_bytes)
    
    return result

def search_for_data(ID:str, column=0, filename="sessions.csv"):
    '''
    Returns the line number in sessions.csv where
    a session with the maching username occurs
    '''
    with open(filename) as f:
        reader = csv.reader(f)

        for i,line in enumerate(reader):
            if line[column] == ID:
                return line
    
    return None

def search_in_fp(ID:str, f, column=0):
    '''
    Returns the line number in sessions.csv where
    a session with the maching username occurs
    '''
    reader = csv.reader(f)

    for i,line in enumerate(reader):
        if line[column] == ID:
            return line
    
    return None