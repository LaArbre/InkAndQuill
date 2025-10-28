# example.py
from orm import *
from datetime import datetime

# ---------------------------
#   Définition des modèles
# ---------------------------
class User(Model):
    id = INTEGER(primary_key=True)
    name = TEXT(not_null=True)
    email = TEXT(default="inconnu@example.com")

class Server(Model):
    id = INTEGER(primary_key=True)
    name = TEXT(not_null=True)
    owner = ForeignKey(User, not_null=True)
    created_at = DATETIME(default=datetime.now)

# ---------------------------
#         Tests ORM
# ---------------------------
def test():
    print("=== Création d'un utilisateur ===")
    alice = User.new(name="Alice", email="alice@example.com")
    bob = User.new(name="Bob")
    print(alice)
    print(bob)

    print("\n=== Création de serveurs liés ===")
    s1 = Server.new(name="Serveur1", owner=alice)
    s2 = Server.new(name="Serveur2", owner=bob)
    s3 = Server.new(name="Serveur3", owner=alice)
    print(s1)
    print(s2)
    print(s3)

    print("\n=== Vérification des ForeignKey ===")
    print(s1.owner.name)  # C'est Alice
    print(s2.owner.name)  # C'est Bob
    print(s3.owner.name)  # C'est Alice

    print("\n=== Récupération de tous les serveurs ===")
    servers = Server.all()
    for srv in servers:
        print(f"{srv.name} -> owner: {srv.owner.name}")

    print("\n=== Modification d'un serveur ===")
    s1.name = "Serveur1-Renamed"
    s1.save()
    srv = Server.get(id=s1.id)
    print(srv)

    print("\n=== Suppression d'un serveur ===")
    s2.delete()
    print("Serveurs restants :", Server.all())

if __name__ == "__main__":
    test()
