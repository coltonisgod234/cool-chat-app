import uuid

def generate_id():
    return str(uuid.uuid4())

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