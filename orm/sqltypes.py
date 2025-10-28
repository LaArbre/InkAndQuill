from datetime import datetime
import json

class SQLType:
    sql_name = "TEXT"

    def __init__(self, primary_key=False, unique=False, not_null=False, default=None):
        self.primary_key = primary_key
        self.unique = unique
        self.not_null = not_null
        self.default = default

    def to_sql(self, value):
        return value

    def from_sql(self, value):
        return value

    def validate(self, value):
        return True

    def sql_definition(self, name):
        parts = [f'"{name}"', self.sql_name]
        if self.primary_key:
            parts.append("PRIMARY KEY AUTOINCREMENT")
        if self.unique:
            parts.append("UNIQUE")
        if self.not_null:
            parts.append("NOT NULL")
        if self.default is not None and not callable(self.default):
            val = f"'{self.default}'" if isinstance(self.default, str) else self.default
            parts.append(f"DEFAULT {val}")
        return " ".join(parts)


class TEXT(SQLType):
    sql_name = "TEXT"
    def validate(self, value):
        return isinstance(value, str) or value is None


class INTEGER(SQLType):
    sql_name = "INTEGER"
    def to_sql(self, value):
        return int(value) if value is not None else None
    def from_sql(self, value):
        return int(value) if value is not None else None
    def validate(self, value):
        return isinstance(value, int) or value is None


class REAL(SQLType):
    sql_name = "REAL"
    def to_sql(self, value):
        return float(value) if value is not None else None
    def from_sql(self, value):
        return float(value) if value is not None else None


class DATETIME(SQLType):
    sql_name = "DATETIME"
    def to_sql(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError("DATETIME attend un objet datetime.")
    def from_sql(self, value):
        return datetime.fromisoformat(value) if value else None


class BOOLEAN(SQLType):
    sql_name = "INTEGER"
    def to_sql(self, value):
        return 1 if value else 0
    def from_sql(self, value):
        return bool(value)


class JSON(SQLType):
    sql_name = "TEXT"
    def to_sql(self, value):
        return json.dumps(value, ensure_ascii=False) if value is not None else None
    def from_sql(self, value):
        return json.loads(value) if value else None


class ForeignKey(SQLType):
    def __init__(self, model_class, not_null=False, default=None):
        super().__init__(primary_key=False, unique=False, not_null=not_null, default=default)
        self.model_class = model_class
        self.sql_name = "INTEGER"

    def to_sql(self, value):
        if value is None:
            return None
        if isinstance(value, self.model_class._child_class):
            return value.id
        return int(value)

    def from_sql(self, value):
        if value is None:
            return None
        obj = self.model_class.get(id=value)
        if obj is None:
            raise ValueError(f"ForeignKey: aucun objet {self.model_class.__name__} trouvé pour id={value}")
        return obj

    def validate(self, value):
        return value is None or isinstance(value, (int, self.model_class._child_class))
