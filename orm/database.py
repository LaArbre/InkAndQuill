import sqlite3
import pymysql
import json
from datetime import datetime
from .types import python_to_sql

def init_log_table(log):
    query = """
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT,
        action TEXT,
        keys TEXT,
        values TEXT,
        timestamp TEXT
    )
    """
    log["cursor"].execute(query)
    log["connect"].commit()

def record_history(log, table_name, action, keys, values):
    log["cursor"].execute("""
        INSERT INTO history (table_name, action, keys, values, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        table_name,
        action,
        ",".join(keys) if isinstance(keys, (list, tuple)) else str(keys),
        json.dumps(values, ensure_ascii=False),
        datetime.now().isoformat()
    ))
    log["connect"].commit()

class Database:
    def __init__(self, mysql_db=False, **kwargs):
        if mysql_db:
            self.data = {
                "connect": pymysql.connect(
                    host=kwargs.get("host", "localhost"),
                    user=kwargs.get("user", "root"),
                    password=kwargs.get("password", ""),
                    database=kwargs.get("database", ""),
                    charset="utf8mb4"
                )
            }
            self.placeholder = "%s"
        else:
            self.data = {"connect": sqlite3.connect(kwargs.get("path", "local.db"))}
            self.placeholder = "?"

        self.data["cursor"] = self.data["connect"].cursor()

        # Logs toujours SQLite
        self.log = {"connect": sqlite3.connect(kwargs.get("log_path", "logs.db"))}
        self.log["cursor"] = self.log["connect"].cursor()
        init_log_table(self.log)

    # --------------------- CRUD ---------------------
    def insert(self, table_name, data: dict, columns_type: dict):
        sql_data = {k: python_to_sql(v, columns_type[k]) for k, v in data.items()}
        keys = ", ".join(sql_data.keys())
        placeholders = ", ".join([self.placeholder] * len(sql_data))
        query = f'INSERT INTO "{table_name}" ({keys}) VALUES ({placeholders})'
        self.data["cursor"].execute(query, tuple(sql_data.values()))
        self.data["connect"].commit()
        record_history(self.log, table_name, "INSERT", sql_data.keys(), sql_data)
        return self.data["cursor"].lastrowid

    def update(self, table_name, data: dict, where: dict, columns_type: dict):
        sql_data = {k: python_to_sql(v, columns_type[k]) for k, v in data.items()}
        set_clause = ", ".join([f'"{k}" = {self.placeholder}' for k in sql_data])
        where_clause = " AND ".join([f'"{k}" = {self.placeholder}' for k in where])
        query = f'UPDATE "{table_name}" SET {set_clause} WHERE {where_clause}'
        self.data["cursor"].execute(query, tuple(sql_data.values()) + tuple(where.values()))
        self.data["connect"].commit()
        record_history(self.log, table_name, "UPDATE", sql_data.keys(), sql_data)

    def delete(self, table_name, where: dict):
        where_clause = " AND ".join([f'"{k}" = {self.placeholder}' for k in where])
        query = f'DELETE FROM "{table_name}" WHERE {where_clause}'
        self.data["cursor"].execute(query, tuple(where.values()))
        self.data["connect"].commit()
        record_history(self.log, table_name, "DELETE", where.keys(), where)

    def select(self, table_name, columns=None, where=None):
        column_part = "*" if not columns else ", ".join(columns)
        where_clause = ""
        params = ()
        if where:
            conditions = [f'"{k}" = {self.placeholder}' for k in where]
            where_clause = f"WHERE {' AND '.join(conditions)}"
            params = tuple(where.values())
        query = f'SELECT {column_part} FROM "{table_name}" {where_clause}'
        self.data["cursor"].execute(query, params)
        return self.data["cursor"].fetchall()

    def create_table(self, table_name, columns: dict):
        col_defs = []
        if "id" not in columns:
            col_defs.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        for col, col_type in columns.items():
            if col != "id":
                col_defs.append(f"{col} {col_type}")
        query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
        self.data["cursor"].execute(query)
        self.data["connect"].commit()

    def close(self):
        self.data["connect"].close()
        self.log["connect"].close()
