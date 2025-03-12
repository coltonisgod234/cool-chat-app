class GuildPermissionEntry:
    def __init__(self, raw:str, user, guild,
                create_channel:bool, delete_channel:bool, manage_channel:bool,
                view_perms:bool, manage_perms:bool, bypass_everything:bool = False,
                owner:bool = True
    ):
        self.raw = raw
        self.username = user
        self.guild = guild
        self.create_channel = create_channel
        self.delete_channel = delete_channel
        self.manage_channel = manage_channel
        self.view_perms = view_perms
        self.manage_perms = manage_perms
        self.bypass_everything = bypass_everything
        self.owner = owner

class ChannelPermissionEntry:
    def __init__(
        self, raw:str, user, channel,
        send_messages:bool, delete_messages:bool, manage_messages:bool,
        view_messages:bool = True
    ):
        self.raw = raw
        self.user = user
        self.channel = channel
        self.send_messages = send_messages
        self.delete_channel = delete_messages
        self.manage_messages = manage_messages
        self.view_messages = view_messages

def highestGuildPerms(username, guild_cid):
    return GuildPermissionEntry(
        raw="",
        user=username,
        guild=guild_cid,
        create_channel=True,
        delete_channel=True,
        manage_channel=True,
        view_perms=True,
        manage_perms=True,
        bypass_everything=True,
        owner=True
    )