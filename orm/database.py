import sqlite3
import pymysql
import json
import os
from datetime import datetime
from .accorder import python_to_sql


def record_history(log, table_name, action, keys, values):
    log["cursor"].execute("""
        INSERT INTO history (table_name, action, keys, text_values, timestamp)
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
    """Gestionnaire bas-niveau des requêtes SQL."""

    def __init__(self):
        if os.getenv("DB_SQL", False):
            self.data = {
                "connect": pymysql.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", ""),
                    database=os.getenv("DB_NAME", ""),
                    charset="utf8mb4"
                )
            }
            self.placeholder = "%s"
        else:
            self.data = {"connect": sqlite3.connect(os.getenv("DB_BASE_PATH", "local.db"))}
            self.placeholder = "?"
        self.data["cursor"] = self.data["connect"].cursor()

        # Journalisation
        self.log = {"connect": sqlite3.connect(os.getenv("DB_LOG_PATH", "logs.db"))}
        self.log["cursor"] = self.log["connect"].cursor()
        self.log["cursor"].execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT,
                action TEXT,
                keys TEXT,
                text_values TEXT,
                timestamp TEXT
            )
        """)
        self.log["connect"].commit()

    # --------------------- CRUD ---------------------
    def insert(self, table_name, data: dict, columns_type: dict):
        sql_data = {k: python_to_sql(v, columns_type[k]) for k, v in data.items()}
        keys = ", ".join([f'"{k}"' for k in sql_data])
        placeholders = ", ".join([self.placeholder] * len(sql_data))
        query = f'INSERT INTO "{table_name}" ({keys}) VALUES ({placeholders})'
        self.data["cursor"].execute(query, tuple(sql_data.values()))
        self.data["connect"].commit()
        record_history(self.log, table_name, "INSERT", list(sql_data.keys()), sql_data)
        return self.data["cursor"].lastrowid

    def update(self, table_name, data: dict, where: dict, columns_type: dict):
        sql_data = {k: python_to_sql(v, columns_type[k]) for k, v in data.items()}
        set_clause = ", ".join([f'"{k}" = {self.placeholder}' for k in sql_data])
        where_clause = " AND ".join([f'"{k}" = {self.placeholder}' for k in where])
        query = f'UPDATE "{table_name}" SET {set_clause} WHERE {where_clause}'
        self.data["cursor"].execute(query, tuple(sql_data.values()) + tuple(where.values()))
        self.data["connect"].commit()
        record_history(self.log, table_name, "UPDATE", list(sql_data.keys()), sql_data)

    def delete(self, table_name, where: dict):
        where_clause = " AND ".join([f'"{k}" = {self.placeholder}' for k in where])
        query = f'DELETE FROM "{table_name}" WHERE {where_clause}'
        self.data["cursor"].execute(query, tuple(where.values()))
        self.data["connect"].commit()
        record_history(self.log, table_name, "DELETE", list(where.keys()), where)

    def select(self, table_name, columns=None, where=None):
        column_part = ", ".join([f'"{c}"' for c in columns]) if columns else "*"
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
        col_defs = [f'"{col}" {typ}' for col, typ in columns.items()]
        query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
        self.data["cursor"].execute(query)
        self.data["connect"].commit()

    def table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.data["cursor"].execute(query, (table_name,))
        return self.data["cursor"].fetchone() is not None

    def close(self):
        self.data["connect"].close()
        self.log["connect"].close()
