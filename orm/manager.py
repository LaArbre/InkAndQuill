from .database import Database
from .types import sql_to_python

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

        def save(self):
            data = {c: getattr(self, c) for c in self.columns}
            if hasattr(self, "id") and self.id:
                self.db.update(self.table_name, data, {"id": self.id}, self.columns)
            else:
                self.id = self.db.insert(self.table_name, data, self.columns)

        def delete(self):
            if not hasattr(self, "id") or not self.id:
                raise ValueError("Objet non enregistré")
            self.db.delete(self.table_name, {"id": self.id})
            self.id = None

        model_class.save = save
        model_class.delete = delete

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
