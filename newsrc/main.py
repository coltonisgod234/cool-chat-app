import messages
import utils
import dbhelpers as db

INFO, WARN, ERROR, CRITICAL = utils.get_loglevels()

sqlengine = db.engine  # THIS IS A REFRENCE, NOT A COPY!
utils.log(INFO, "Creating tables...")
db.Base.metadata.create_all(sqlengine)

# Create user
u = messages.User("colton", "abc")
db_user = db.User.create(u.username, u.password, u.cid)
u.force_logon()
db_user.update_token(u.token)

# Create guild and channel
g = messages.Guild()
db_guild = db.Guild.create(g.cid)

c = messages.Channel("general")
db_channel = db.Channel.create(c.name, g.cid, c.cid)
db_guild.add_channel(db_channel)

# Add message
m = messages.Message(u, "Hello!", "")
db_message = db.Message.create(m.content, c.cid, m.cid)
db_channel.add_message(db_message)