"""
Tracks URLs consulted during research for NotebookLM export.

Records: URL, title, university, category, query date, domain classification.
No user identification data is stored.
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DB_PATH = Path(__file__).parent.parent / "data" / "sources.db"
_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                university TEXT,
                category TEXT,
                consulted_at REAL NOT NULL,
                is_official_domain INTEGER DEFAULT 0,
                UNIQUE(url, university)
            )
        """)
        _conn.commit()
    return _conn


def _is_official_edu_domain(url: str) -> bool:
    try:
        domain = urlparse(url).netloc.lower()
        return ".edu" in domain
    except Exception:
        return False


def record_source(
    url: str,
    university: str | None = None,
    title: str | None = None,
    category: str | None = None,
) -> None:
    """Record a consulted URL. Silently ignores duplicates."""
    if not url or not url.startswith("http"):
        return
    conn = _get_conn()
    is_official = 1 if _is_official_edu_domain(url) else 0
    try:
        conn.execute(
            """INSERT OR IGNORE INTO sources (url, title, university, category, consulted_at, is_official_domain)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (url, title, university, category, time.time(), is_official),
        )
        conn.commit()
    except sqlite3.Error:
        pass


def get_sources(
    university: str | None = None,
    category: str | None = None,
    official_only: bool = False,
) -> list[dict[str, Any]]:
    """Query recorded sources with optional filters."""
    conn = _get_conn()
    query = "SELECT url, title, university, category, consulted_at, is_official_domain FROM sources WHERE 1=1"
    params: list[Any] = []
    if university:
        query += " AND university = ?"
        params.append(university)
    if category:
        query += " AND category = ?"
        params.append(category)
    if official_only:
        query += " AND is_official_domain = 1"
    query += " ORDER BY consulted_at DESC"
    rows = conn.execute(query, params).fetchall()
    return [
        {
            "url": r[0], "title": r[1], "university": r[2],
            "category": r[3], "consulted_at": r[4],
            "is_official_domain": bool(r[5]),
        }
        for r in rows
    ]


def export_sources(
    university: str | None = None,
    category: str | None = None,
    official_only: bool = False,
) -> dict[str, str]:
    """Export sources in three formats. Returns dict of filename -> content."""
    sources = get_sources(university=university, category=category, official_only=False)
    official_sources = [s for s in sources if s["is_official_domain"]]

    # Filter for the requested subset
    if official_only:
        target = official_sources
    else:
        target = sources

    # urls.txt
    urls_txt = "\n".join(s["url"] for s in target) + "\n" if target else ""

    # urls-oficiais.txt
    urls_oficiais = "\n".join(s["url"] for s in official_sources) + "\n" if official_sources else ""

    # fontes.md
    lines = ["# Fontes consultadas\n"]
    for s in target:
        oficial_tag = " [OFICIAL]" if s["is_official_domain"] else ""
        from datetime import datetime
        dt = datetime.fromtimestamp(s["consulted_at"]).strftime("%Y-%m-%d")
        lines.append(f"- **{s.get('title') or 'Sem título'}**{oficial_tag}")
        lines.append(f"  - URL: {s['url']}")
        lines.append(f"  - Universidade: {s.get('university') or 'N/A'}")
        lines.append(f"  - Categoria: {s.get('category') or 'N/A'}")
        lines.append(f"  - Data: {dt}")
        lines.append("")
    fontes_md = "\n".join(lines)

    return {
        "urls.txt": urls_txt,
        "urls-oficiais.txt": urls_oficiais,
        "fontes.md": fontes_md,
    }
