from orm import *

# --- Définition d’un modèle ---
class User(Model):
    name: "TEXT"
    email: "TEXT"
    age: "INTEGER"


class Server(Model):
    name: "TEXT"
    token: "INTEGER"

# --- Création d’une ligne ---
alice = User.new(name="Alice", email="alice@example.com", age=25)
print(alice)

q = Server.new(name= "ooo", token= 123)
# <UserRow {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'age': 25}>

# --- Mise à jour ---
alice.age = 26
alice.save()

# --- Lecture ---
bob = User.get(name="Bob")
print(bob)

# --- Suppression ---

# --- Tous les utilisateurs ---
for u in Server.all():
    print(u)
