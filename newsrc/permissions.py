class GuildPermissionEntry:
    def __init__(self, raw:str, user, guild,
                create_channel:bool, delete_channel:bool, manage_channel:bool,
                view_perms:bool, manage_perms:bool,
    ):
        self.raw = raw
        self.user = username
        self.guild = guild
        self.create_channel = create_channel
        self.delete_channel = delete_channel
        self.manage_channel = manage_channel
        self.view_perms = view_perms
        self.manage_perms = manage_perms

class ChannelPermissionEntry:
    def __init__(
        self, raw:str, user, channel,
        send_messages:bool, delete_messages:bool, manage_messages:bool
    ):
        self.raw = raw
        self.user = user
        self.channel = channel
        self.send_messages = send_messages
        self.delete_channel = delete_messages
        self.manage_messages = manage_messages
