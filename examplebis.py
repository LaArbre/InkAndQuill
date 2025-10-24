from orm import *
from datetime import datetime

class User(Model):
    name = TEXT(not_null=True)

class Server(Model):
    name = TEXT(not_null=True)
    owner = ForeignKey(User, not_null=True)
    created_at = DATETIME(default=datetime.now)

alice = User.new(name="Alice")
s = Server.new(name="MonServeur", owner=alice)

print(alice.id)           # 1
print(s.id)               # 1
print(s.owner.name)       # Alice
