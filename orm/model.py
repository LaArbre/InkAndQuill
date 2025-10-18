from .accorder import sql_to_python

class Model():
    table_name: str = None
    columns: dict = {}
    db = None

    def __init__(self, id=None, create=True, **kwargs):
        self.id = id
        if self.id is not None and self.db:
            row = self.db.select(self.table_name, columns=list(self.columns.keys()), where={"id": self.id})
            if row:
                for col, val in zip(self.columns.keys(), row[0]):
                    setattr(self, col, sql_to_python(val, self.columns[col]))
        elif create:
            for col in self.columns:
                setattr(self, col, kwargs.get(col))

    def save(self):
        """Sauvegarde l'objet en base de données"""
        if not self.db:
            raise ValueError("Model non enregistré auprès d'un DBManager")
        data = {c: getattr(self, c) for c in self.columns if hasattr(self, c)}
        data_without_id = {k: v for k, v in data.items() if k != "id" and v is not None}
        if not data_without_id:
            raise ValueError("Aucune donnée à sauvegarder")
        
        if hasattr(self, "id") and self.id:
            self.db.update(self.table_name, data, {"id": self.id}, self.columns)
        else:
            self.id = self.db.insert(self.table_name, data, self.columns)

    def delete(self):
        """Supprime l'objet de la base de données"""
        if not self.db:
            raise ValueError("Model non enregistré auprès d'un DBManager")
        if not hasattr(self, "id") or not self.id:
            raise ValueError("Objet non enregistré")
        
        self.db.delete(self.table_name, {"id": self.id})
        self.id = None