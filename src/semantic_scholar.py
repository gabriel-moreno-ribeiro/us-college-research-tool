"""
Cliente para a Semantic Scholar API (Allen Institute for AI).

API pública e gratuita: https://api.semanticscholar.org/
Sem API key obrigatória, mas o rate limit sem key é agressivo (~1 req/seg
e picos podem levar a 429). Uma key gratuita (opcional) aumenta o limite:
https://www.semanticscholar.org/product/api#api-key-form

Usado para: dado o nome de um professor + afiliação, encontrar seu perfil
de autor, publicações recentes, áreas de pesquisa e coautores.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from . import cache

BASE_URL = "https://api.semanticscholar.org/graph/v1"


@dataclass
class SemanticScholarClient:
    api_key: str | None = field(default_factory=lambda: os.environ.get("SEMANTIC_SCHOLAR_API_KEY"))
    session: requests.Session = field(default_factory=requests.Session)
    min_delay_seconds: float = 3.5  # respeita rate limit sem key (1 req/seg oficial, margem extra)
    max_retries: int = 5

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self.api_key} if self.api_key else {}

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        for attempt in range(self.max_retries):
            resp = self.session.get(url, params=params, headers=self._headers(), timeout=20)
            if resp.status_code == 429:
                wait = self.min_delay_seconds * (2 ** attempt)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            time.sleep(self.min_delay_seconds)
            return resp.json()
        raise RuntimeError(f"Rate limit persistente na Semantic Scholar API: {url}")

    def get_paper_by_doi(self, doi: str) -> dict[str, Any] | None:
        """Busca um paper específico pelo DOI — muito mais preciso que busca por nome."""
        cache_key = f"doi:{doi}"
        cached = cache.get("semantic_scholar", cache_key, max_age_days=7)
        if cached is not None:
            return cached
        try:
            result = self._get(
                f"/paper/DOI:{doi}",
                {"fields": "title,year,venue,citationCount,url,authors"},
            )
            if result:
                cache.put("semantic_scholar", cache_key, result)
            return result
        except (RuntimeError, requests.HTTPError):
            return None

    def search_author(self, name: str, affiliation_hint: str | None = None) -> list[dict[str, Any]]:
        """Busca autores por nome. Reordena por afiliação + relevância acadêmica."""
        cache_key = f"author:{name.lower().strip()}"
        cached = cache.get("semantic_scholar", cache_key, max_age_days=7)
        if cached is not None:
            results = cached
        else:
            data = self._get(
                "/author/search",
                {"query": name, "fields": "name,affiliations,paperCount,citationCount,hIndex,url"},
            )
            results = data.get("data", [])
            cache.put("semantic_scholar", cache_key, results)
        if affiliation_hint:
            hint = affiliation_hint.lower()
            hint_words = set(hint.split())

            def score(a: dict[str, Any]) -> tuple[int, int, int]:
                affs = " ".join(a.get("affiliations") or []).lower()
                aff_match = 2 if hint in affs else (1 if hint_words & set(affs.split()) else 0)
                h = a.get("hIndex") or 0
                papers = a.get("paperCount") or 0
                return (aff_match, h, papers)

            results.sort(key=score, reverse=True)
        return results

    def get_author_papers(
        self, author_id: str, limit: int = 10, fields: str | None = None
    ) -> list[dict[str, Any]]:
        """Retorna os papers mais recentes/relevantes de um autor."""
        fields = fields or "title,year,venue,abstract,citationCount,url,authors"
        cache_key = f"papers:{author_id}:{limit}"
        cached = cache.get("semantic_scholar", cache_key, max_age_days=7)
        if cached is not None:
            return cached
        data = self._get(
            f"/author/{author_id}/papers",
            {"fields": fields, "limit": limit},
        )
        papers = data.get("data", [])
        papers.sort(key=lambda p: (p.get("year") or 0), reverse=True)
        cache.put("semantic_scholar", cache_key, papers)
        return papers

    def find_professor_research(
        self, name: str, affiliation_hint: str | None = None, paper_limit: int = 5
    ) -> dict[str, Any] | None:
        """
        Fluxo completo: nome do professor -> melhor match de autor -> papers recentes.
        Retorna None se não encontrar nenhum autor correspondente.
        """
        candidates = self.search_author(name, affiliation_hint=affiliation_hint)
        if not candidates:
            return None
        best = candidates[0]
        papers = self.get_author_papers(best["authorId"], limit=paper_limit)
        return {
            "name": best.get("name"),
            "affiliations": best.get("affiliations"),
            "h_index": best.get("hIndex"),
            "citation_count": best.get("citationCount"),
            "paper_count": best.get("paperCount"),
            "profile_url": best.get("url"),
            "recent_papers": papers,
        }


def format_professor_research(data: dict[str, Any]) -> str:
    if not data:
        return "Nenhum resultado encontrado no Semantic Scholar."
    lines = [
        f"### {data['name']}",
        f"- Afiliações conhecidas: {', '.join(data.get('affiliations') or []) or 'N/D'}",
        f"- h-index: {data.get('h_index', 'N/D')} | Citações totais: {data.get('citation_count', 'N/D')} "
        f"| Papers publicados: {data.get('paper_count', 'N/D')}",
        f"- Perfil: {data.get('profile_url', 'N/D')}",
        "",
        "**Publicações recentes:**",
    ]
    for p in data.get("recent_papers", []):
        year = p.get("year", "s/d")
        title = p.get("title", "sem título")
        venue = p.get("venue") or ""
        cites = p.get("citationCount", 0)
        lines.append(f"  - ({year}) {title} — {venue} — {cites} citações")
    return "\n".join(lines)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, stream=__import__("sys").stderr)
    client = SemanticScholarClient()
    result = client.find_professor_research("Regina Barzilay", affiliation_hint="MIT")
    logging.info(format_professor_research(result) if result else "Não encontrado.")
