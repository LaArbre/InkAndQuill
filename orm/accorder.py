from datetime import datetime


def sql_to_python(value, col_type):
    if value is None:
        return None
    if "INTEGER" in col_type:
        return int(value)
    elif "REAL" in col_type:
        return float(value)
    elif "TEXT" in col_type:
        return str(value)
    elif "DATETIME" in col_type:
        return datetime.fromisoformat(value)
    return value


def python_to_sql(value, col_type):
    if value is None:
        return None
    if "DATETIME" in col_type and isinstance(value, datetime):
        return value.isoformat()
    return value
