import json
from dataclasses import dataclass

@dataclass
class GuildPermission:
    user_id: str
    guild_id: str
    create_channel: bool = False
    delete_channel: bool = False 
    manage_channel: bool = False
    view_perms: bool = False
    manage_perms: bool = False
    bypass_everything: bool = False
    owner: bool = False
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "guild_id": self.guild_id,
            "create_channel": self.create_channel,
            "delete_channel": self.delete_channel,
            "manage_channel": self.manage_channel,
            "view_perms": self.view_perms,
            "manage_perms": self.manage_perms,
            "bypass_everything": self.bypass_everything,
            "owner": self.owner
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["user_id"],
            guild_id=data["guild_id"],
            create_channel=data.get("create_channel", False),
            delete_channel=data.get("delete_channel", False),
            manage_channel=data.get("manage_channel", False),
            view_perms=data.get("view_perms", False),
            manage_perms=data.get("manage_perms", False),
            bypass_everything=data.get("bypass_everything", False),
            owner=data.get("owner", False)
        )
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_data):
        return cls.from_dict(json.loads(json_data))

@dataclass
class ChannelPermission:
    user_id: str
    channel_id: str
    send_messages: bool = False
    delete_messages: bool = False
    manage_messages: bool = False
    view_messages: bool = True
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "send_messages": self.send_messages,
            "delete_messages": self.delete_messages,
            "manage_messages": self.manage_messages,
            "view_messages": self.view_messages
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["user_id"],
            channel_id=data["channel_id"],
            send_messages=data.get("send_messages", False),
            delete_messages=data.get("delete_messages", False),
            manage_messages=data.get("manage_messages", False),
            view_messages=data.get("view_messages", True)
        )
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_data):
        return cls.from_dict(json.loads(json_data))

def create_admin_guild_permission(user_id, guild_id):
    """Create admin-level guild permissions for a user"""
    return GuildPermission(
        user_id=user_id,
        guild_id=guild_id,
        create_channel=True,
        delete_channel=True,
        manage_channel=True,
        view_perms=True,
        manage_perms=True,
        bypass_everything=True,
        owner=True
    )

def create_default_channel_permission(user_id, channel_id):
    """Create default channel permissions for a user"""
    return ChannelPermission(
        user_id=user_id,
        channel_id=channel_id,
        send_messages=True,
        delete_messages=False,
        manage_messages=False,
        view_messages=True
    ) 