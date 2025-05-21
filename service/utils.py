import uuid
import inspect
import time
from typing import Dict, List, Optional, Any
import json

# Logging levels
INFO = "info"
WARN = "warn"
ERROR = "error"
CRITICAL = "critical"
VERBOSE = "verbose"
DEBUG = "debug"

SHOW_VERBOSE = True
PREVIOUS_LOOKBACK = 2

def get_loglevels():
    """Returns a list of available log levels"""
    return [INFO, WARN, ERROR, CRITICAL, VERBOSE, DEBUG]

def log(severity, message):
    """Log a message with a specific severity level"""
    print(f"{round(time.time_ns()): <22} {prev_running_func(2): <20}:      {severity:>8}         {message}")

def prev_running_func(n=1):
    """Get the name of the previous running function in the call stack"""
    stk = inspect.stack()
    f = stk[n]
    
    # Extract class/module context if applicable
    qualname = getattr(f.function, '__qualname__', f.function)
    
    return qualname

def generate_id():
    """Generate a unique ID for resources"""
    x = str(uuid.uuid4())
    log(INFO, f"Generated a new CID, {x} for function {prev_running_func(PREVIOUS_LOOKBACK)}")
    return x

def get_timestamp():
    """Get the current timestamp as a string"""
    return str(time.time())

def get_request_token(request):
    """Extract the authorization token from a Flask request"""
    headers = request.headers
    bearer = headers.get("Authorization")
    if not bearer:
        return None
        
    parts = bearer.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
        
    return parts[1]

def user_in_guild(guild, username):
    """Check if a user is a member of a guild"""
    if guild.permissions.get(username) == None:
        return False
    
    return True

def can_view_channel(channel, username):
    """Check if a user can view a channel"""
    perm = channel.permissions.get(username)
    if perm == None:
        return None
    
    if perm.view_messages == True:
        return True
    
    else:
        return False

def check_permission(obj, key, permission):
    """Generic permission check function"""
    try:
        return obj.permissions[key].__getattribute__(permission)
    except (KeyError, AttributeError):
        return None
        
def from_json(json_str, default=None):
    """Convert JSON string to Python object"""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default
        
def to_json(obj):
    """Convert Python object to JSON string"""
    return json.dumps(obj) 