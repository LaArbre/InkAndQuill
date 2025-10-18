from .database import Database
from .accorder import sql_to_python

class DBManager:
    def __init__(self, path="local.db", log_path="logs.db"):
        self.db = Database(path=path, log_path=log_path)
        self.models = {}

    def register_model(self, model_class):
        self.models[model_class.__name__] = model_class
        model_class.db = self.db

        self.db.create_table(
            table_name=model_class.table_name,
            columns=model_class.columns
        )

    def create(self, model_class, **kwargs):
        obj = model_class(**kwargs)
        obj.save()
        return obj

    def get(self, model_class, id):
        row = self.db.select(model_class.table_name, columns=list(model_class.columns.keys()), where={"id": id})
        if not row:
            return None
        data = {col: sql_to_python(val, model_class.columns[col]) for col, val in zip(model_class.columns.keys(), row[0])}
        obj = model_class(**data)
        obj.id = id
        return obj

    def close(self):
        self.db.close()

# Instance globale
manager = DBManager()