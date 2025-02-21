import messages
import utils
import dbhelpers as db

INFO, WARN, ERROR, CRITICAL = utils.get_loglevels()

sqlengine = db.engine  # THIS IS A REFRENCE, NOT A COPY!
utils.log(INFO, "Creating tables...")
db.Base.metadata.create_all(sqlengine)  # Attempt to create tables

u = messages.User("colton", "abc")
db.add_user(u)
u.force_logon()

g = messages.Guild()
c = messages.Channel("general")
g.add_channel(c)

m = messages.Message(u, "Hello!", "")

c.add_message(m)