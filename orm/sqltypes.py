from datetime import datetime
import json


class SQLType:
    sql_name = "TEXT"  # par défaut

    def to_sql(self, value):
        return value

    def from_sql(self, value):
        return value

    def validate(self, value):
        return True


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
