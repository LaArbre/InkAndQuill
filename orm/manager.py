# manager.py
from .database import Database

class DBManager:
    def __init__(self):
        self.db = Database()

    def register_class(self, model_class):
        if self.db.table_exists(model_class.__name__):
            model_class._db = self.db
            return
        model_class._db = self.db
        # On récupère le type SQL pour chaque colonne
        columns_sql = {name: col.sql_name for name, col in model_class._columns.items()}
        self.db.create_table(model_class.__name__, columns_sql)

    def create(self, model_class, **kwargs):
        obj = model_class.new(**kwargs)
        return obj

    def get(self, model_class, **where):
        return model_class.get(**where)

    def all(self, model_class):
        return model_class.all()

    def delete(self, model_class, **where):
        model_class.delete(**where)

    def close(self):
        self.db.close()


# Instance globale du manager
manager = DBManager()
