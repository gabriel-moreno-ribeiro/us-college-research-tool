"""
Cache local baseado em SQLite para evitar bater nas APIs repetidamente.

Tabela genérica: (source, key) → value_json + fetched_at.
Cada módulo usa um 'source' diferente (ex: "scorecard", "orcid", "semantic_scholar").
TTL é configurável por consulta — dados de admissão mudam pouco (30 dias),
papers mudam mais (7 dias).
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent.parent / "data" / "cache.db"

_conn: sqlite3.Connection | None = None
_enabled: bool = True


def set_enabled(enabled: bool) -> None:
    global _enabled
    _enabled = enabled


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                source TEXT NOT NULL,
                key TEXT NOT NULL,
                value_json TEXT NOT NULL,
                fetched_at REAL NOT NULL,
                PRIMARY KEY (source, key)
            )
        """)
        _conn.commit()
    return _conn


def get(source: str, key: str, max_age_days: float = 30.0) -> Any | None:
    """Retorna o valor cacheado ou None se não existir / estiver expirado."""
    if not _enabled:
        return None
    conn = _get_conn()
    row = conn.execute(
        "SELECT value_json, fetched_at FROM cache WHERE source = ? AND key = ?",
        (source, key),
    ).fetchone()
    if row is None:
        return None
    value_json, fetched_at = row
    age_days = (time.time() - fetched_at) / 86400
    if age_days > max_age_days:
        return None
    return json.loads(value_json)


def put(source: str, key: str, value: Any) -> None:
    """Salva um valor no cache."""
    if not _enabled:
        return
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO cache (source, key, value_json, fetched_at) VALUES (?, ?, ?, ?)",
        (source, key, json.dumps(value, ensure_ascii=False), time.time()),
    )
    conn.commit()
