from .types import sql_to_python

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        return new_cls

class Model(metaclass=ModelMeta):
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
