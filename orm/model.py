from .database import Database
from .sqltypes import *

database = Database()


class ParentModel:
    def __init_subclass__(cls, **kwargs):
        """Configuration automatique des sous-classes par modèles"""

        # Étape 1 -> Récupérer toutes les colonnes SQL définies dans la classe
        cls._columns = {
            name: value
            for name, value in cls.__dict__.items()
            if hasattr(value, "sql_definition")
        }

        # Étape 2 -> Vérifier les clés primaires
        primary_keys = [name for name, col in cls._columns.items() if getattr(col, "primary_key", False)]
        if len(primary_keys) == 0:
            raise ValueError(f"La classe {cls.__name__} doit avoir une clé primaire.")
        if len(primary_keys) > 1:
            raise ValueError(f"La classe {cls.__name__} ne peut avoir qu'une seule clé primaire (trouvé {primary_keys}).")

        # Étape 3 -> Créer dynamiquement la classe enfant (row model)
        cls._child_class = type(
            f"_{cls.__name__}Row",
            (ChildModel,),
            {"_parent": cls, "_columns": cls._columns}
        )

        # Étape 4 -> Enregistrer la table dans la base
        database.create_table(cls.__name__, cls._columns)

    # ============================================================
    #                        MÉTHODES ORM
    # ============================================================

    @classmethod
    def new(cls, **kwargs):
        """Crée une nouvelle entrée dans la base"""

        data = {}

        # Étape 1 -> Vérifier que la clé primaire n'est pas insérée manuellement
        for name, col in cls._columns.items():
            if getattr(col, "primary_key", False) and name in kwargs:
                raise ValueError(f"La clé primaire '{name}' est auto-incrémentée et ne doit pas être insérée manuellement.")

        # Étape 2 -> Appliquer les valeurs par défaut et valider
        for k, col in cls._columns.items():
            if getattr(col, "primary_key", False):
                continue

            value = kwargs.get(k, None)
            if value is None:
                value = col.default() if callable(col.default) else col.default

            # Étape 3 -> Validation du type
            if not col.validate(value):
                raise TypeError(f"Colonne '{k}' attend {col.sql_name}, pas {type(value).__name__}")

            data[k] = col.to_sql(value)

        # Étape 4 -> Insertion en base
        row_id = database.insert(cls.__name__, data)
        pk_name = next(name for name, col in cls._columns.items() if getattr(col, "primary_key", False))
        data[pk_name] = row_id

        # Étape 5 -> Conversion SQL -> Python
        for k, v in data.items():
            col = cls._columns[k]
            data[k] = col.from_sql(v)

        # Étape 6 -> Retour de l'objet
        return cls._child_class(**data)

    @classmethod
    def get(cls, **where):
        """Récupère une ligne unique selon un filtre"""

        if not where or not isinstance(where, dict):
            raise ValueError("Le paramètre 'where' doit être un dictionnaire non vide.")

        rows = database.select(cls.__name__, where=where)
        if not rows:
            return None

        data = dict(zip(cls._columns.keys(), rows[0]))

        for k, v in data.items():
            col = cls._columns[k]
            data[k] = col.from_sql(v)

        return cls._child_class(**data)

    @classmethod
    def all(cls):
        """Récupère toutes les lignes de la table"""

        rows = database.select(cls.__name__)
        result = []

        for row in rows:
            data = dict(zip(cls._columns.keys(), row))
            for k, v in data.items():
                col = cls._columns[k]
                data[k] = col.from_sql(v)
            result.append(cls._child_class(**data))

        return result

    @classmethod
    def delete(cls, **where):
        """Supprime des lignes"""

        if not where or not isinstance(where, dict):
            raise ValueError("Le paramètre 'where' doit être un dictionnaire non vide.")
        database.delete(cls.__name__, where)


class ChildModel:
    _parent = None
    _columns = {}

    def __init__(self, **kwargs):
        """Assigner les valeurs aux attributs"""

        for col, value in kwargs.items():
            object.__setattr__(self, col, value)

    def __getattribute__(self, name):
        """Gérer les ForeignKey de manière paresseuse"""

        val = object.__getattribute__(self, name)
        columns = object.__getattribute__(self, "_columns")
        col = columns.get(name)

        if isinstance(col, ForeignKey):
            if val is None:
                return None
            if isinstance(val, int):
                obj = col.from_sql(val)
                object.__setattr__(self, name, obj)
                return obj
            return val
        return val

    def save(self):
        pk_name = next(name for name, col in self._columns.items() if getattr(col, "primary_key", False))
        pk_value = getattr(self, pk_name, None)
        if pk_value is None:
            raise ValueError("Impossible de sauvegarder : aucune clé primaire.")

        data = {c: self._columns[c].to_sql(getattr(self, c)) for c in self._columns if c != pk_name}
        database.update(self._parent.__name__, data, {pk_name: pk_value})

    def delete(self):
        pk_name = next(name for name, col in self._columns.items() if getattr(col, "primary_key", False))
        pk_value = getattr(self, pk_name, None)
        if pk_value is None:
            raise ValueError("Impossible de supprimer : aucune clé primaire.")

        database.delete(self._parent.__name__, {pk_name: pk_value})
        setattr(self, pk_name, None)

    def __repr__(self):
        """Afficher joliment les valeurs"""
        cols = {c: getattr(self, c, None) for c in self._columns}
        return f"<{self._parent.__name__}Row {cols}>"
