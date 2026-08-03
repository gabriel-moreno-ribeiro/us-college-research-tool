"""
Cliente para a DBLP API (https://dblp.org/faq/).

DBLP é a bibliografia canônica de ciência da computação. Cobertura de faculty
de CS/ECE é muito superior a ORCID e cobre publicações que muitos professores
não mantêm no ORCID. API pública sem chave.

Endpoints usados:
- Search: https://dblp.org/search/author/api?q=<name>&format=json
- Person publications: https://dblp.org/pid/<PID>.xml
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any

import requests

from . import cache

SEARCH_URL = "https://dblp.org/search/author/api"
PID_XML_TEMPLATE = "https://dblp.org/pid/{pid}.xml"


@dataclass
class DblpAuthor:
    pid: str  # DBLP internal ID (e.g. "95/2040")
    name: str
    affiliation: str | None  # As reported by DBLP (may be None)
    url: str  # Canonical DBLP URL


@dataclass
class DblpPublication:
    title: str
    year: int | None
    venue: str | None
    pub_type: str  # 'inproceedings', 'article', etc.


@dataclass
class DblpClient:
    session: requests.Session = field(default_factory=requests.Session)
    min_delay_seconds: float = 1.0
    max_retries: int = 3

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any] | None:
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(
                    url, params=params, timeout=20,
                    headers={"Accept": "application/json"},
                )
                if resp.status_code == 429:
                    time.sleep(self.min_delay_seconds * (2 ** attempt))
                    continue
                resp.raise_for_status()
                time.sleep(self.min_delay_seconds)
                return resp.json()
            except requests.RequestException:
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(self.min_delay_seconds * (2 ** attempt))
        return None

    def _get_text(self, url: str) -> str | None:
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, timeout=20)
                if resp.status_code == 429:
                    time.sleep(self.min_delay_seconds * (2 ** attempt))
                    continue
                resp.raise_for_status()
                time.sleep(self.min_delay_seconds)
                return resp.text
            except requests.RequestException:
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(self.min_delay_seconds * (2 ** attempt))
        return None

    def search_author(self, name: str, max_results: int = 5) -> list[DblpAuthor]:
        """Search DBLP for authors matching a name. Returns candidates with
        DBLP-reported affiliation when available."""
        cache_key = f"search:{name.lower().strip()}"
        cached = cache.get("dblp", cache_key, max_age_days=30)
        if cached is not None:
            return [DblpAuthor(**a) for a in cached]

        data = self._get_json(SEARCH_URL, {"q": name, "format": "json", "h": max_results})
        if not data:
            return []

        hits = (
            data.get("result", {})
            .get("hits", {})
            .get("hit", [])
        )
        # DBLP sometimes returns a dict instead of a list when only one hit
        if isinstance(hits, dict):
            hits = [hits]

        authors: list[DblpAuthor] = []
        for h in hits:
            info = h.get("info", {}) or {}
            # PID is embedded in the URL like "https://dblp.org/pid/95/2040"
            url_str = info.get("url", "") or ""
            pid = ""
            if "/pid/" in url_str:
                pid = url_str.split("/pid/", 1)[1].strip("/")

            # Affiliation can be under notes.note.text (single) or a list.
            affiliation = None
            notes = info.get("notes")
            if isinstance(notes, dict):
                note = notes.get("note")
                if isinstance(note, dict) and note.get("@type") == "affiliation":
                    affiliation = note.get("text")
                elif isinstance(note, list):
                    for n in note:
                        if isinstance(n, dict) and n.get("@type") == "affiliation":
                            affiliation = n.get("text")
                            break

            if pid:
                authors.append(DblpAuthor(
                    pid=pid,
                    name=info.get("author", "") or "",
                    affiliation=affiliation,
                    url=url_str,
                ))

        cache.put("dblp", cache_key, [
            {"pid": a.pid, "name": a.name, "affiliation": a.affiliation, "url": a.url}
            for a in authors
        ])
        return authors

    def get_publications(self, pid: str, limit: int = 10) -> list[DblpPublication]:
        """Fetch a DBLP person's publications, sorted newest first."""
        cache_key = f"pubs:{pid}:{limit}"
        cached = cache.get("dblp", cache_key, max_age_days=7)
        if cached is not None:
            return [DblpPublication(**p) for p in cached]

        xml_text = self._get_text(PID_XML_TEMPLATE.format(pid=pid))
        if not xml_text:
            return []

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        pubs: list[DblpPublication] = []
        for r in root.findall("r"):
            children = list(r)
            if not children:
                continue
            entry = children[0]
            title_el = entry.find("title")
            year_el = entry.find("year")
            venue_el = entry.find("booktitle")
            if venue_el is None:
                venue_el = entry.find("journal")

            title = (title_el.text or "").strip().rstrip(".") if title_el is not None else ""
            year = None
            if year_el is not None and year_el.text:
                try:
                    year = int(year_el.text.strip())
                except ValueError:
                    pass
            venue = (venue_el.text or "").strip() if venue_el is not None else None

            if title:
                pubs.append(DblpPublication(
                    title=title, year=year, venue=venue, pub_type=entry.tag,
                ))

        pubs.sort(key=lambda p: p.year or 0, reverse=True)
        pubs = pubs[:limit]

        cache.put("dblp", cache_key, [
            {"title": p.title, "year": p.year, "venue": p.venue, "pub_type": p.pub_type}
            for p in pubs
        ])
        return pubs

    def find_professor(
        self, name: str, affiliation_hint: str,
    ) -> tuple[DblpAuthor, str] | None:
        """
        Find the DBLP author matching name + affiliation.
        Returns (author, confidence) where confidence is 'high' if DBLP's own
        affiliation matches, 'medium' if only one author with the given name,
        or None if no plausible match.
        """
        candidates = self.search_author(name)
        if not candidates:
            return None

        hint_lower = affiliation_hint.lower()
        # Drop generic institutional words — they match unrelated universities
        # (e.g. "university" alone would match "Technical University of Dortmund").
        _generic = {"university", "college", "school", "institute", "of", "the",
                    "and", "for", "at", "state"}
        hint_tokens = [
            t for t in hint_lower.split()
            if len(t) > 3 and t not in _generic
        ]

        # Prefer authors whose DBLP-reported affiliation contains the hint.
        for c in candidates:
            if c.affiliation and hint_lower in c.affiliation.lower():
                return c, "high"

        # Second pass: distinctive-token overlap
        for c in candidates:
            if c.affiliation and hint_tokens:
                aff_lower = c.affiliation.lower()
                if any(t in aff_lower for t in hint_tokens):
                    return c, "high"

        # No affiliation match: return top candidate but flag as low confidence
        # (only one candidate is "medium", multiple candidates without affiliation
        # match is genuinely uncertain).
        if len(candidates) == 1:
            return candidates[0], "medium"
        return candidates[0], "low"
