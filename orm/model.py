# model.py
from .database import database
from .sqltypes import ForeignKey, INTEGER

class ParentModel:
    _db = database

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        columns = {
            name: value
            for name, value in cls.__dict__.items()
            if hasattr(value, "sql_definition")
        }

        columns["id"] = INTEGER(primary_key=True)
        cls._columns = columns

        cls._child_class = type(
            f"_{cls.__name__}Row",
            (ChildModel,),
            {"_parent": cls, "_columns": cls._columns}
        )

        # Création de la table
        columns_sql = {name: col.sql_definition(name) for name, col in cls._columns.items()}
        cls._db.register_class(cls)
        cls._db.create_table(cls.__name__, columns_sql)

    @classmethod
    def new(cls, **kwargs):
        data = {}
        for k, col in cls._columns.items():
            if k == "id":
                raise
            value = kwargs.get(k, None)
            if value is None:
                if callable(col.default):
                    value = col.default()
                else:
                    value = col.default
            if not col.validate(value):
                raise TypeError(f"Colonne '{k}' attend {col.sql_name}, pas {type(value).__name__}")
            data[k] = col.to_sql(value)

        data["id"] = cls._db.insert(cls.__name__, data, cls._columns)

        # Convertit les valeurs en objets Python
        for k, v in data.items():
            col = cls._columns[k]
            if isinstance(col, ForeignKey):
                if isinstance(kwargs.get(k), col.model_class._child_class):
                    data[k] = kwargs.get(k)
                else:
                    data[k] = col.from_sql(v)
            else:
                data[k] = col.from_sql(v)

        return cls._child_class(**data)

    @classmethod
    def get(cls, **where):
        rows = cls._db.select(cls.__name__, where=where)
        if not rows:
            return None
        data = dict(zip(cls._columns.keys(), rows[0]))
        for k, v in data.items():
            col = cls._columns[k]
            if isinstance(col, ForeignKey):
                data[k] = col.from_sql(v)
            else:
                data[k] = col.from_sql(v)
        return cls._child_class(**data)

    @classmethod
    def all(cls):
        rows = cls._db.select(cls.__name__)
        result = []
        for row in rows:
            data = dict(zip(cls._columns.keys(), row))
            for k, v in data.items():
                col = cls._columns[k]
                if isinstance(col, ForeignKey):
                    data[k] = col.from_sql(v)
                else:
                    data[k] = col.from_sql(v)
            result.append(cls._child_class(**data))
        return result

    @classmethod
    def delete(cls, **where):
        cls._db.delete(cls.__name__, where)


class ChildModel:
    _parent = None
    _columns = {}

    def __init__(self, **kwargs):
        for col, value in kwargs.items():
            object.__setattr__(self, col, value)

    def __getattribute__(self, name):
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
        db = self._parent._db
        if not getattr(self, "id", None):
            raise ValueError("Impossible de sauvegarder : aucun ID.")
        data = {c: self._columns[c].to_sql(getattr(self, c)) for c in self._columns if c != "id"}
        db.update(self._parent.__name__, data, {"id": self.id}, self._columns)

    def delete(self):
        db = self._parent._db
        if not getattr(self, "id", None):
            raise ValueError("Impossible de supprimer : aucun ID.")
        db.delete(self._parent.__name__, {"id": self.id})
        self.id = None

    def __repr__(self):
        cols = {c: getattr(self, c, None) for c in self._columns}
        return f"<{self._parent.__name__}Row {cols}>"
