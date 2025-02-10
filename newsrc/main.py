import messages
import utils
import dbhelpers as db
import logging

INFO, WARN, ERROR, CRITICAL, VERBOSE, VERBOSEX = utils.get_loglevels()

db.Base.metadata.create_all(db.engine)

u = messages.User("colton", "abc")
u.database_counterpart = db.create_user_counterpart(u)

g = messages.Guild()

c = messages.Channel("general")
g.add_channel(c)

m = messages.Message(u, "Hello!", "")
c.add_message(m)