from ..data.repositories import MessageRepository, ChannelRepository, GuildRepository, UserRepository
from ..domain.models import InMemoryMessage, InMemoryChannel, InMemoryGuild
from ..domain.permissions import create_admin_guild_permission, create_default_channel_permission
from . import utils
import time

class ChatService:
    def __init__(self, 
                 message_repo: MessageRepository, 
                 channel_repo: ChannelRepository,
                 guild_repo: GuildRepository,
                 user_repo: UserRepository):
        self.message_repo = message_repo
        self.channel_repo = channel_repo
        self.guild_repo = guild_repo
        self.user_repo = user_repo
        
        # In-memory cache
        self.guilds = {}  # cid -> InMemoryGuild
        self.channels = {} # cid -> InMemoryChannel
        
    # Guild operations
    def create_guild(self, creator_username: str):
        """Create a new guild with the specified user as owner"""
        # Create the guild
        guild = InMemoryGuild()
        
        # Get user by username
        user = self.user_repo.get_user_by_username(creator_username)
        if not user:
            raise ValueError(f"User {creator_username} not found")
            
        # Set permissions
        admin_perms = create_admin_guild_permission(user.cid, guild.cid)
        guild.permissions[creator_username] = admin_perms
        
        # Store in memory
        self.guilds[guild.cid] = guild
        
        # Store in DB (if using DB)
        self.guild_repo.create_guild({creator_username: admin_perms.to_dict()})
        
        return guild.cid
        
    def delete_guild(self, guild_cid: str, username: str):
        """Delete a guild if the user has permissions"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        if not utils.user_in_guild(guild, username):
            raise PermissionError("Not a member of this guild")
            
        # Check if user has permissions to delete
        user_perms = guild.permissions.get(username)
        if not (user_perms and (user_perms.owner or user_perms.bypass_everything)):
            raise PermissionError("No permission to delete guild")
            
        # Delete all channels in the guild
        for channel_cid in list(guild.channels.keys()):
            self.delete_channel(guild_cid, channel_cid, username)
            
        # Remove from memory
        del self.guilds[guild_cid]
        
        # Remove from DB
        self.guild_repo.delete_guild(guild_cid)
        
        return True
        
    # Channel operations
    def create_channel(self, guild_cid: str, channel_name: str, username: str):
        """Create a new channel in a guild"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        if not utils.user_in_guild(guild, username):
            raise PermissionError("Not a member of this guild")
            
        # Check if user has permission to create channels
        user_perms = guild.permissions.get(username)
        if not (user_perms and (user_perms.create_channel or user_perms.owner or user_perms.bypass_everything)):
            raise PermissionError("No permission to create channels")
            
        # Create channel
        channel = InMemoryChannel(channel_name)
        
        # Set default permission for the creator
        user = self.user_repo.get_user_by_username(username)
        channel.permissions[username] = create_default_channel_permission(user.cid, channel.cid)
        
        # Add to guild
        guild.add_channel(channel)
        
        # Store in memory
        self.channels[channel.cid] = channel
        
        # Store in DB
        self.channel_repo.create_channel(
            guild_id=guild_cid,
            name=channel_name,
            permissions_json=utils.to_json({username: channel.permissions[username].to_dict()})
        )
        
        return channel.cid
        
    def delete_channel(self, guild_cid: str, channel_cid: str, username: str):
        """Delete a channel from a guild"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        channel = guild.channels.get(channel_cid)
        if not channel:
            raise ValueError(f"Channel {channel_cid} not found in guild {guild_cid}")
            
        if not utils.user_in_guild(guild, username):
            raise PermissionError("Not a member of this guild")
            
        # Check permissions
        user_guild_perms = guild.permissions.get(username)
        user_channel_perms = channel.permissions.get(username)
        
        has_permission = (
            (user_guild_perms and (user_guild_perms.delete_channel or user_guild_perms.owner or user_guild_perms.bypass_everything)) or
            (user_channel_perms and user_channel_perms.delete_messages)
        )
        
        if not has_permission:
            raise PermissionError("No permission to delete this channel")
            
        # Delete messages in the channel
        # (This would also be handled by DB CASCADE if using a database)
        
        # Remove from guild
        guild.delete_channel(channel_cid)
        
        # Remove from memory
        if channel_cid in self.channels:
            del self.channels[channel_cid]
            
        # Remove from DB
        self.channel_repo.delete_channel(channel_cid)
        
        return True
        
    def get_channels_in_guild(self, guild_cid: str, username: str):
        """Get list of channels in a guild"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        if not utils.user_in_guild(guild, username):
            raise PermissionError("Not a member of this guild")
            
        # Return list of channel IDs
        return list(guild.channels.keys())
        
    # Message operations
    def send_message(self, guild_cid: str, channel_cid: str, username: str, content: str):
        """Send a message to a channel"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        channel = guild.channels.get(channel_cid)
        if not channel:
            raise ValueError(f"Channel {channel_cid} not found in guild {guild_cid}")
            
        if not utils.user_in_guild(guild, username):
            raise PermissionError("Not a member of this guild")
            
        # Check channel view permission
        user_perms = channel.permissions.get(username)
        if not (user_perms and user_perms.send_messages):
            guild_perms = guild.permissions.get(username)
            if not (guild_perms and (guild_perms.owner or guild_perms.bypass_everything)):
                raise PermissionError("No permission to send messages in this channel")
                
        # Get user
        user = self.user_repo.get_user_by_username(username)
        if not user:
            raise ValueError(f"User {username} not found")
            
        # Create message
        timestamp = time.time()
        message = InMemoryMessage(user, content, timestamp)
        
        # Add to channel
        channel.add_message(message)
        
        # Store in DB
        self.message_repo.create_message(
            author_cid=user.cid,
            channel_cid=channel_cid,
            content=content,
            timestamp=str(timestamp)
        )
        
        return message.cid
        
    def get_messages(self, guild_cid: str, channel_cid: str, username: str, limit: int = 50):
        """Get messages from a channel"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        channel = guild.channels.get(channel_cid)
        if not channel:
            raise ValueError(f"Channel {channel_cid} not found in guild {guild_cid}")
            
        if not utils.user_in_guild(guild, username):
            raise PermissionError("Not a member of this guild")
            
        # Check view permission
        user_perms = channel.permissions.get(username)
        guild_perms = guild.permissions.get(username)
        
        has_permission = (
            (user_perms and user_perms.view_messages) or
            (guild_perms and (guild_perms.owner or guild_perms.bypass_everything))
        )
        
        if not has_permission:
            raise PermissionError("No permission to view messages in this channel")
            
        # Return messages IDs
        return list(channel.messages.keys())
        
    def delete_message(self, guild_cid: str, channel_cid: str, message_cid: str, username: str):
        """Delete a message"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        channel = guild.channels.get(channel_cid)
        if not channel:
            raise ValueError(f"Channel {channel_cid} not found in guild {guild_cid}")
            
        message = channel.messages.get(message_cid)
        if not message:
            raise ValueError(f"Message {message_cid} not found")
            
        if not utils.user_in_guild(guild, username):
            raise PermissionError("Not a member of this guild")
            
        # Check permissions - either message author or has delete permission
        is_author = message.author.username == username
        user_perms = channel.permissions.get(username)
        guild_perms = guild.permissions.get(username)
        
        has_permission = (
            is_author or
            (user_perms and user_perms.delete_messages) or
            (guild_perms and (guild_perms.owner or guild_perms.bypass_everything))
        )
        
        if not has_permission:
            raise PermissionError("No permission to delete this message")
            
        # Delete message
        channel.delete_message(message_cid)
        
        # Remove from DB
        self.message_repo.delete_message(message_cid)
        
        return True
        
    def edit_message(self, guild_cid: str, channel_cid: str, message_cid: str, username: str, new_content: str):
        """Edit a message"""
        guild = self.guilds.get(guild_cid)
        if not guild:
            raise ValueError(f"Guild {guild_cid} not found")
            
        channel = guild.channels.get(channel_cid)
        if not channel:
            raise ValueError(f"Channel {channel_cid} not found in guild {guild_cid}")
            
        message = channel.messages.get(message_cid)
        if not message:
            raise ValueError(f"Message {message_cid} not found")
            
        # Only the author or admins can edit messages
        is_author = message.author.username == username
        guild_perms = guild.permissions.get(username)
        
        has_permission = (
            is_author or
            (guild_perms and (guild_perms.owner or guild_perms.bypass_everything))
        )
        
        if not has_permission:
            raise PermissionError("No permission to edit this message")
            
        # Create new message with updated content
        new_message = InMemoryMessage(
            author=message.author,
            content=new_content,
            timestamp=message.timestamp,
            cid=message_cid
        )
        
        # Update message
        channel.edit_message(message_cid, new_message)
        
        # Update in DB
        self.message_repo.update_message_content(message_cid, new_content)
        
        return True 