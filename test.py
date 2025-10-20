# models.py
from orm import Model

class User(Model):
    __columns__ = {
        "name": "TEXT",
        "email": "TEXT",
        "age": "INTEGER"
    }

u = User(name="Alice", email="alice@mail.com", age=22)
u.save()

u.name = "eeeeeee"
u.save()

print(u)            # <User {'id': 1, 'name': 'Alice', 'email': 'alice@mail.com', 'age': 22}>
print(User.all())   # liste complète des utilisateurs
