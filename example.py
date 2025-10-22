# example.py
from orm import *
from datetime import datetime

# ------------------ Définition de la table ------------------
class User(Model):
    name = TEXT
    age = INTEGER
    is_admin = BOOLEAN
    created_at = DATETIME

# ------------------ Test de création ------------------
print("=== Création ===")
alice = User.new(name="Alice", age=25, is_admin=False, created_at=datetime.now())
bob = User.new(name="Bob", age=30, is_admin=True, created_at=datetime.now())
print(alice)
print(bob)

# ------------------ Test de lecture ------------------
print("\n=== Lecture ===")
u = User.get(id=alice.id)
print(u)

# ------------------ Test de liste complète ------------------
print("\n=== Tous les utilisateurs ===")
users = User.all()
for user in users:
    print(user)

# ------------------ Test de modification ------------------
print("\n=== Modification ===")
alice.age = 26
alice.is_admin = True
alice.save()
updated = User.get(id=alice.id)
print(updated)

# ------------------ Test de suppression ------------------
print("\n=== Suppression ===")
bob.delete()
all_users = User.all()
for user in all_users:
    print(user)