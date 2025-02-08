import uuid
import inspect
import time

def generate_id():
    x = str(uuid.uuid4())
    log("info", f"Generated a new CID: {x}")
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
    print(f"at {round(time.time())} in {last_running_func(): <20}:      {severity}         {message}")

def last_running_func(n=2):
    stk = inspect.stack()
    f = stk[n]  # Use 2 instead of 1 to avoid detecting log() or last_running_func()
    
    return f.function

def get_loglevels():
    return ["info", "warn", "error", "critcal"]