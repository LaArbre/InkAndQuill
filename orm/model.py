from .accorder import sql_to_python
from .manager import manager


class ParentModel:
    """
    Représente une table SQL.
    Chaque sous-classe définit simplement des attributs annotés :
        class User(ParentModel):
            name: "TEXT"
            email: "TEXT"
            age: "INTEGER"
    """

    _db = manager
    _columns = {}
    _child_class = None

    # -------------------- Configuration automatique --------------------

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        annotations = getattr(cls, "__annotations__", {})
        cls._columns = {k: v for k, v in annotations.items()}

        if "id" not in cls._columns:
            cls._columns["id"] = "INTEGER PRIMARY KEY AUTOINCREMENT"

        cls._child_class = type(
            f"_{cls.__name__}Row",
            (ChildModel,),
            {"_parent": cls, "_columns": cls._columns}
        )

        cls._db.register_class(cls)

    # -------------------- Méthodes principales --------------------

    @classmethod
    def new(cls, **kwargs):
        """Crée une nouvelle ligne et l’enregistre en base"""
        if not cls._db:
            raise ValueError(f"{cls.__name__} n'est pas lié à un gestionnaire de base de données.")

        # Données valides (sans l'id)
        data = {k: v for k, v in kwargs.items() if k in cls._columns and k != "id"}
        new_id = cls._db.insert(cls.__name__, data, cls._columns)

        # Crée une instance enfant liée
        return cls._child_class(id=new_id, **kwargs)

    @classmethod
    def get(cls, **where):
        """Récupère une ligne selon une condition"""
        rows = cls._db.select(cls.__name__, where=where)
        if not rows:
            return None

        data = dict(zip(cls._columns.keys(), rows[0]))
        return cls._child_class(**data)

    @classmethod
    def all(cls):
        """Retourne toutes les lignes sous forme d'objets"""
        rows = cls._db.select(cls.__name__)
        return [cls._child_class(**dict(zip(cls._columns.keys(), row))) for row in rows]

    @classmethod
    def delete(cls, **where):
        """Supprime les lignes correspondant à une condition"""
        cls._db.delete(cls.__name__, where)


class ChildModel:
    """
    Représente une seule ligne d’un ParentModel.
    N’a jamais accès directement au gestionnaire : tout passe par le parent.
    """

    _parent = None
    _columns = {}

    def __init__(self, **kwargs):
        for col in self._columns:
            setattr(self, col, kwargs.get(col, None))

    def save(self):
        """Met à jour la ligne en base via le parent."""
        db = self._parent._db
        if not getattr(self, "id", None):
            raise ValueError("Impossible de sauvegarder : aucun ID.")
        data = {c: getattr(self, c) for c in self._columns if c != "id"}
        db.update(self._parent.__name__, data, {"id": self.id}, self._columns)

    def delete(self):
        """Supprime cette ligne de la base."""
        db = self._parent._db
        if not getattr(self, "id", None):
            raise ValueError("Impossible de supprimer : aucun ID.")
        db.delete(self._parent.__name__, {"id": self.id})
        self.id = None

    def __repr__(self):
        cols = {c: getattr(self, c, None) for c in self._columns}
        return f"<{self._parent.__name__}Row {cols}>"
