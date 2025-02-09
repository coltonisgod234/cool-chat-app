import messages
import utils
import dbhelpers as db
import logging

INFO, WARN, ERROR, CRITICAL, VERBOSE, VERBOSEX = utils.get_loglevels()

sqlengine = db.engine  # THIS IS A REFRENCE, NOT A COPY!
utils.log(INFO, "Creating tables...")
db.Base.metadata.create_all(sqlengine)  # Attempt to create tables

dbm = db.DatabaseManagement("example.db")

u = messages.User("colton", "abc")
dbm.add_user(u)

g = messages.Guild()
dbm.add_guild(g)

print(dbm.get_guild(g).channels)

c = messages.Channel("general")
g.add_channel(c)
dbm.add_channel(c)
dbm.attach_channel(c, g)

print(dbm.get_guild(g).channels)

m = messages.Message(u, "Hello!", "")

c.add_message(m)