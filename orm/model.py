from .accorder import sql_to_python
from .manager import manager


class Model:
    """
    Classe de base pour tous les modèles ORM.
    Chaque sous-classe représente une table SQL.
    """

    _db = None
    _columns = {}

    def __init_subclass__(cls, **kwargs):
        """
        Appelé automatiquement quand une classe hérite de Model.
        Enregistre la table correspondante dans la base.
        """
        super().__init_subclass__(**kwargs)

        # Récupération des colonnes déclarées dans la sous-classe
        if not hasattr(cls, "__columns__"):
            raise AttributeError(f"Le modèle {cls.__name__} doit définir un attribut __columns__")

        # Ajout automatique d'une clé primaire
        cls._columns = dict(cls.__columns__)
        if "id" not in cls._columns:
            cls._columns["id"] = "INTEGER PRIMARY KEY AUTOINCREMENT"

        # Enregistrement auprès du manager
        manager.register_class(cls)

    def __init__(self, **kwargs):
        """Initialise un objet Model (soit depuis la base, soit en mémoire)."""
        self._db = self.__class__._db

        # Si une ligne correspondante existe déjà → la charger
        if "id" in kwargs:
            row = self._db.select(self.__class__.__name__, where={"id": kwargs["id"]})
            if row:
                for col, val in zip(self._columns.keys(), row[0]):
                    setattr(self, col, sql_to_python(val, self._columns[col]))
                return

        # Sinon → nouvelle instance
        for col in self._columns:
            setattr(self, col, kwargs.get(col, None))

    # -------------------- CRUD --------------------

    def save(self):
        """Sauvegarde l'objet en base de données."""
        if not self._db:
            raise ValueError("Model non enregistré auprès d'un DBManager")

        data = {c: getattr(self, c) for c in self._columns if getattr(self, c, None) is not None}
        data_without_id = {k: v for k, v in data.items() if k != "id"}

        if not data_without_id:
            raise ValueError("Aucune donnée à sauvegarder")

        if getattr(self, "id", None):
            self._db.update(self.__class__.__name__, data, {"id": self.id}, self._columns)
        else:
            self.id = self._db.insert(self.__class__.__name__, data_without_id, self._columns)

    def delete(self):
        """Supprime l'objet de la base de données."""
        if not self._db:
            raise ValueError("Model non enregistré auprès d'un DBManager")
        if not getattr(self, "id", None):
            raise ValueError("Objet non enregistré")

        self._db.delete(self.__class__.__name__, {"id": self.id})
        self.id = None

    # -------------------- Utilitaires --------------------

    @classmethod
    def get(cls, **where):
        """Récupère un objet par condition."""
        row = cls._db.select(cls.__name__, where=where)
        if not row:
            return None
        data = dict(zip(cls._columns.keys(), row[0]))
        return cls(**data)

    @classmethod
    def all(cls):
        """Récupère tous les enregistrements."""
        rows = cls._db.select(cls.__name__)
        return [cls(**dict(zip(cls._columns.keys(), r))) for r in rows]

    def __repr__(self):
        cols = {c: getattr(self, c, None) for c in self._columns}
        return f"<{self.__class__.__name__} {cols}>"
