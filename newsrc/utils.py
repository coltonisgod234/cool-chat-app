import uuid
import inspect
import time

SHOW_VERBOSE = True
PREVIOUS_LOOKBACK = 2

def get_username_by_token(token, users):
    try:
        data = [username for username, object in users.items() if object.token == token][0]
        print(token, users, users.items(), data)
        return data
    except IndexError as e:
        print("Cant index into users dict: IndexError| ", e)
        print(token, users, users.items())
        return None

def get_request_token(request):
    headers = request.headers
    bearer = headers.get("Authorization")
    token = bearer.split()[1]
    return token

def generate_id():
    x = str(uuid.uuid4())
    log("info", f"Generated a new CID, {x} for function {prev_running_func(PREVIOUS_LOOKBACK)}")
    return x

def edit_permission(obj, key, entry):
    obj.permissions[key] = entry
    return obj

def grant_permission(obj, key, permission):
    o = obj.permissions[key]
    o.__setattr__(permission, True)

    obj.permissions[key] = o
    return obj

def revoke_permission(obj, key, permission):
    o = obj.permissions[key]
    o.__setattr__(permission, False)

    obj.permissions[key] = o
    return obj

def check_permission(obj, key, permission):
    try:
        return obj.permissions[key].__getattribute__(permission)
    except KeyError:
        return None

def log(severity, message):
    print(f"{round(time.time_ns()): <22} {prev_running_func(2): <20}:      {severity:>8}         {message}")

def prev_running_func(n=1):
    stk = inspect.stack()
    f = stk[n]

    # Extract class/module context if applicable
    qualname = getattr(f.function, '__qualname__', f.function)
    
    return qualname

def get_loglevels():
    return ["info", "warn", "error", "critcal", "verbose", "debug"]

def try_index(obj, index):
    try:
        data = obj[index]
        return data
    except IndexError:
        return None