"""
Generic JSON-backed SQLite store used to persist operational
state for in-memory domain stores.

Each store maps to its own table (``store_<name>``) with a text
primary key and a JSON-encoded value. Persistence is disabled in
the test environment so test isolation is preserved.
"""

import json
import sqlite3
from pathlib import Path
from threading import Lock

from app.core.config import settings


def persistence_enabled() -> bool:
    """
    Whether disk persistence is active for the current run.
    """

    return (
        settings.PERSISTENCE_ENABLED
        and settings.ENVIRONMENT.lower() != "test"
    )


def new_store(name: str) -> "SqliteStore | None":
    """
    Create a new SqliteStore instance if persistence is enabled.
    """
    if persistence_enabled():
        return SqliteStore(name)
    return None


class SqliteStore:
    """
    A single-table key/value store backed by SQLite.
    """

    def __init__(
        self,
        name: str,
        db_path: str | Path | None = None,
    ) -> None:

        self._name = name
        self._path = Path(
            db_path or settings.PERSISTENCE_DB_PATH
        )
        self._lock = Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @property
    def _table(self) -> str:
        return f"store_{self._name}"

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {self._table} ("
                "key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )

    def save(
        self,
        key: str,
        value: dict,
    ) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    f"INSERT INTO {self._table}(key, value) "
                    "VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, json.dumps(value)),
                )

    def save_many(
        self,
        items: list[tuple[str, dict]],
    ) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.executemany(
                    f"INSERT INTO {self._table}(key, value) "
                    "VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    [
                        (key, json.dumps(value))
                        for key, value in items
                    ],
                )

    def get(
        self,
        key: str,
    ) -> dict | None:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    f"SELECT value FROM {self._table} WHERE key = ?",
                    (key,),
                ).fetchone()
                if row is None:
                    return None
                return json.loads(row[0])

    def all(self) -> list[dict]:
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    f"SELECT value FROM {self._table} ORDER BY key"
                ).fetchall()
                return [json.loads(row[0]) for row in rows]

    def delete(
        self,
        key: str,
    ) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    f"DELETE FROM {self._table} WHERE key = ?",
                    (key,),
                )

    def clear(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(f"DELETE FROM {self._table}")
