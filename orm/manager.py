from .database import Database
from .accorder import sql_to_python


class DBManager:
    """Gestionnaire global des modèles et de la base de données."""

    def __init__(self):
        self.db = Database()

    def register_class(self, model_class):
        """Enregistre une classe de modèle et crée la table si besoin."""
        if self.db.table_exists(model_class.__name__):
            model_class._db = self.db
            return
        model_class._db = self.db
        self.db.create_table(model_class.__name__, model_class._columns)

    def create(self, model_class, **kwargs):
        """Crée et sauvegarde un objet du modèle donné."""
        obj = model_class(**kwargs)
        obj.save()
        return obj

    def get(self, model_class, id):
        """Récupère un objet par ID."""
        row = self.db.select(model_class.__name__, where={"id": id})
        if not row:
            return None
        data = {col: sql_to_python(val, model_class._columns[col]) for col, val in zip(model_class._columns.keys(), row[0])}
        return model_class(**data)

    def close(self):
        self.db.close()


# Instance globale du manager
manager = DBManager()
