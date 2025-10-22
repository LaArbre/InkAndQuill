from .manager import manager
from .sqltypes import *
class ParentModel:
    _db = manager

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Récupère toutes les colonnes SQL
        columns = {}
        for name, value in cls.__dict__.items():
            if name.startswith("_"):
                continue
            # Si c'est une classe SQLType, instancie-la
            if isinstance(value, type) and issubclass(value, SQLType):
                columns[name] = value()
            # Si c'est déjà une instance SQLType
            elif isinstance(value, SQLType):
                columns[name] = value

        # Ajoute la clé primaire si manquante
        if "id" not in columns:
            col_id = INTEGER()
            col_id.sql_name = "INTEGER PRIMARY KEY AUTOINCREMENT"
            columns["id"] = col_id

        cls._columns = columns

        # Crée la classe enfant (ligne)
        cls._child_class = type(
            f"_{cls.__name__}Row",
            (ChildModel,),
            {"_parent": cls, "_columns": cls._columns}
        )

        # Enregistre la table dans la base
        cls._db.register_class(cls)

    # ------------------ Méthodes principales ------------------
    @classmethod
    def new(cls, **kwargs):
        """Crée une nouvelle ligne et l’enregistre en base"""
        data = {}
        for k, v in kwargs.items():
            if k not in cls._columns or k == "id":
                continue
            col = cls._columns[k]
            if not col.validate(v):
                raise TypeError(f"Colonne '{k}' attend {col.sql_name}, pas {type(v).__name__}")
            data[k] = col.to_sql(v)

        if not data:
            raise ValueError(f"Aucune colonne valide fournie pour {cls.__name__}")

        # Insertion dans la base
        new_id = cls._db.insert(cls.__name__, data, cls._columns)

        # Récupère les valeurs converties depuis SQL pour l'objet final
        for k, v in data.items():
            data[k] = cls._columns[k].from_sql(v)
        data["id"] = new_id

        return cls._child_class(**data)

    @classmethod
    def get(cls, **where):
        """Récupère une ligne selon une condition"""
        rows = cls._db.select(cls.__name__, where=where)
        if not rows:
            return None
        data = {k: cls._columns[k].from_sql(v) for k, v in zip(cls._columns.keys(), rows[0])}
        return cls._child_class(**data)

    @classmethod
    def all(cls):
        """Retourne toutes les lignes sous forme d'objets"""
        rows = cls._db.select(cls.__name__)
        result = []
        for row in rows:
            data = {k: cls._columns[k].from_sql(v) for k, v in zip(cls._columns.keys(), row)}
            result.append(cls._child_class(**data))
        return result

    @classmethod
    def delete(cls, **where):
        """Supprime les lignes correspondant à une condition"""
        cls._db.delete(cls.__name__, where)


# ----------------------- Child Model -----------------------
class ChildModel:
    _parent = None
    _columns = {}

    def __init__(self, **kwargs):
        for col in self._columns:
            setattr(self, col, kwargs.get(col, None))

    def save(self):
        db = self._parent._db
        if not getattr(self, "id", None):
            raise ValueError("Impossible de sauvegarder : aucun ID.")
        data = {c: self._columns[c].to_sql(getattr(self, c)) for c in self._columns if c != "id"}
        db.update(self._parent.__name__, data, {"id": self.id}, self._columns)
        # Met à jour les valeurs locales depuis SQL
        for k, v in data.items():
            setattr(self, k, self._columns[k].from_sql(v))

    def delete(self):
        db = self._parent._db
        if not getattr(self, "id", None):
            raise ValueError("Impossible de supprimer : aucun ID.")
        db.delete(self._parent.__name__, {"id": self.id})
        self.id = None

    def to_dict(self):
        return {c: getattr(self, c, None) for c in self._columns}

    def __repr__(self):
        cols = {c: getattr(self, c, None) for c in self._columns}
        return f"<{self._parent.__name__}Row {cols}>"