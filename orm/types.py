from datetime import datetime

def sql_to_python(value, col_type):
    if value is None:
        return None
    if col_type == "INTEGER":
        return int(value)
    elif col_type == "REAL":
        return float(value)
    elif col_type == "TEXT":
        return str(value)
    elif col_type == "DATETIME":
        return datetime.fromisoformat(value)
    return value

def python_to_sql(value, col_type):
    if value is None:
        return None
    if col_type == "DATETIME" and isinstance(value, datetime):
        return value.isoformat()
    return value
