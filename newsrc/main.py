import messages
import utils
import dbhelpers as db
import logging

INFO, WARN, ERROR, CRITICAL, VERBOSE, VERBOSEX = utils.get_loglevels()

db.Base.metadata.create_all(db.engine)


# Create a user
u = messages.User("colton", "abc")
u.database_counterpart = db.create_user_counterpart(u)

# Create a guild
g = messages.Guild()
guild_db = db.create_guild(g.cid)

# Add a channel
c = messages.Channel("general")
g.add_channel(c)
db_ch = guild_db.create_channel(c.cid)

m = messages.Message(u, "Hello!", "")
c.add_message(m)
db_ch.add_message(m)
