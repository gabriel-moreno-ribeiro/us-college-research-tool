"""
Cliente para a OpenAlex API (https://docs.openalex.org/).

OpenAlex é um índice aberto de literatura acadêmica. Cobertura ampla de todas
as áreas, disambiguação por instituição, gratuita, sem chave. Fornece h-index,
works_count e a lista de trabalhos.

Endpoints usados:
- https://api.openalex.org/authors?search=<name>&per-page=N
- https://api.openalex.org/works?filter=author.id:<A_ID>&sort=publication_year:desc

Etiqueta polida via header User-Agent com email (opt-in) para o polite pool,
que dá rate limit maior. Sem isso ainda funciona no pool comum.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from . import cache
from .source_tracker import record_source

BASE_URL = "https://api.openalex.org"


@dataclass
class OpenAlexAuthor:
    author_id: str  # "https://openalex.org/A5077304920"
    name: str
    institutions: list[str]  # last_known_institutions display names
    works_count: int
    h_index: int | None


@dataclass
class OpenAlexPublication:
    title: str
    year: int | None
    venue: str | None
    doi: str | None
    cited_by_count: int


@dataclass
class OpenAlexClient:
    session: requests.Session = field(default_factory=requests.Session)
    min_delay_seconds: float = 0.3
    max_retries: int = 3

    def _headers(self) -> dict[str, str]:
        # OpenAlex "polite pool" — set mailto for higher rate limit
        email = os.environ.get("OPENALEX_MAILTO") or os.environ.get("CONTACT_EMAIL")
        ua = "college-research-tool/1.0"
        if email:
            ua = f"{ua} (mailto:{email})"
        return {"User-Agent": ua}

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any] | None:
        url = f"{BASE_URL}{path}"
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, params=params, headers=self._headers(), timeout=20)
                if resp.status_code == 429:
                    time.sleep(self.min_delay_seconds * (2 ** attempt))
                    continue
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                time.sleep(self.min_delay_seconds)
                return resp.json()
            except requests.RequestException:
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(self.min_delay_seconds * (2 ** attempt))
        return None

    def search_author(self, name: str, per_page: int = 10) -> list[OpenAlexAuthor]:
        cache_key = f"author:{name.lower().strip()}"
        cached = cache.get("openalex", cache_key, max_age_days=30)
        if cached is not None:
            return [OpenAlexAuthor(**a) for a in cached]

        data = self._get("/authors", {"search": name, "per-page": per_page})
        if not data:
            return []

        authors: list[OpenAlexAuthor] = []
        for a in data.get("results", []):
            insts = [
                i.get("display_name", "")
                for i in (a.get("last_known_institutions") or [])
            ]
            authors.append(OpenAlexAuthor(
                author_id=a.get("id", ""),
                name=a.get("display_name", ""),
                institutions=[i for i in insts if i],
                works_count=a.get("works_count") or 0,
                h_index=(a.get("summary_stats") or {}).get("h_index"),
            ))

        # Track OpenAlex search
        if authors:
            record_source(
                url="https://openalex.org/",
                title=f"OpenAlex - Author Search: {name}",
                university=None,
                category="research"
            )

        cache.put("openalex", cache_key, [
            {
                "author_id": a.author_id, "name": a.name,
                "institutions": a.institutions,
                "works_count": a.works_count, "h_index": a.h_index,
            }
            for a in authors
        ])
        return authors

    def get_publications(self, author_id: str, limit: int = 10) -> list[OpenAlexPublication]:
        """Fetch the newest publications for an OpenAlex author."""
        # author_id may be full URL or bare ID
        aid = author_id.rstrip("/").rsplit("/", 1)[-1]
        cache_key = f"pubs:{aid}:{limit}"
        cached = cache.get("openalex", cache_key, max_age_days=7)
        if cached is not None:
            return [OpenAlexPublication(**p) for p in cached]

        data = self._get(
            "/works",
            {
                "filter": f"author.id:{aid}",
                "sort": "publication_year:desc",
                "per-page": limit,
                "select": "title,publication_year,primary_location,doi,cited_by_count",
            },
        )
        if not data:
            return []

        pubs: list[OpenAlexPublication] = []
        for w in data.get("results", []):
            title = w.get("title") or ""
            year = w.get("publication_year")
            doi = w.get("doi")
            if doi and doi.startswith("https://doi.org/"):
                doi = doi[len("https://doi.org/"):]
            venue = None
            loc = w.get("primary_location") or {}
            src = loc.get("source") or {}
            if src:
                venue = src.get("display_name")
            if title:
                pubs.append(OpenAlexPublication(
                    title=title.strip(), year=year, venue=venue, doi=doi,
                    cited_by_count=w.get("cited_by_count") or 0,
                ))

        cache.put("openalex", cache_key, [
            {
                "title": p.title, "year": p.year, "venue": p.venue,
                "doi": p.doi, "cited_by_count": p.cited_by_count,
            }
            for p in pubs
        ])
        return pubs

    def find_professor(
        self, name: str, affiliation_hint: str,
    ) -> tuple[OpenAlexAuthor, str] | None:
        """
        Find the OpenAlex author matching name + affiliation.
        Returns (author, confidence): 'high' if institution matches the hint,
        'medium' if only one candidate, 'low' otherwise.
        """
        candidates = self.search_author(name)
        if not candidates:
            return None

        hint_lower = affiliation_hint.lower()
        hint_tokens = [t for t in hint_lower.split() if len(t) > 3]

        for c in candidates:
            for inst in c.institutions:
                if hint_lower in inst.lower():
                    return c, "high"

        for c in candidates:
            for inst in c.institutions:
                inst_lower = inst.lower()
                if any(t in inst_lower for t in hint_tokens):
                    return c, "high"

        if len(candidates) == 1:
            return candidates[0], "medium"
        return candidates[0], "low"
