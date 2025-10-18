import orm

a = orm.manager

class User(orm.Model):
    table_name="Users"
    columns = {
        "name": "TEXT",
        "email": "TEXT"
    }

class Server(orm.Model):
    table_name="Servers"
    columns = {
        "name": "TEXT",
        "email": "TEXT"
    }

a.register_model(User)
a.register_model(Server)

b:User = a.get(User, 2)
print(b)