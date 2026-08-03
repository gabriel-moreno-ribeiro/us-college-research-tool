"""
Cliente para a API pública do ORCID (https://pub.orcid.org/v3.0/).

ORCID é um identificador aberto e persistente para pesquisadores. A API pública
não requer autenticação para leitura — basta aceitar application/json.

Usado para: dado o nome de um professor + afiliação, encontrar o ORCID iD correto
e extrair a lista de trabalhos publicados (com DOIs quando disponíveis), resolvendo
o problema de desambiguação de homônimos que a busca por nome no Semantic Scholar
não consegue resolver de forma confiável.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import requests

from . import cache

BASE_URL = "https://pub.orcid.org/v3.0"
HEADERS = {"Accept": "application/json"}


@dataclass
class OrcidWork:
    title: str
    year: int | None
    doi: str | None
    work_type: str | None


@dataclass
class OrcidProfile:
    orcid_id: str
    name: str
    affiliations: list[str]
    works: list[OrcidWork]


@dataclass
class OrcidClient:
    session: requests.Session = field(default_factory=requests.Session)
    min_delay_seconds: float = 1.0
    max_retries: int = 3

    def _get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, params=params, headers=HEADERS, timeout=20)
                if resp.status_code == 404:
                    return None
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

    def search_by_name_and_affiliation(
        self, name: str, affiliation: str, max_results: int = 5
    ) -> list[dict[str, Any]]:
        """
        Busca candidatos no ORCID expanded-search.
        Retorna lista de candidatos com orcid-id, given-names, family-name, institution-name.
        """
        cache_key = f"search:{name.lower().strip()}@{affiliation.lower().strip()}"
        cached = cache.get("orcid", cache_key, max_age_days=30)
        if cached is not None:
            return cached

        parts = name.strip().split()
        if len(parts) >= 2:
            given = parts[0]
            family = " ".join(parts[1:])
            query = f'given-names:{given} AND family-name:{family} AND affiliation-org-name:{affiliation}'
        else:
            query = f'name:{name} AND affiliation-org-name:{affiliation}'

        data = self._get(
            f"{BASE_URL}/expanded-search/",
            params={"q": query, "rows": max_results},
        )
        if not data:
            return []
        results = data.get("expanded-result", []) or []
        cache.put("orcid", cache_key, results)
        return results

    def get_profile(self, orcid_id: str) -> OrcidProfile | None:
        """Busca o registro completo de um ORCID iD e extrai nome, afiliações e works."""
        cache_key = f"profile:{orcid_id}"
        cached = cache.get("orcid", cache_key, max_age_days=7)
        if cached is not None:
            return OrcidProfile(
                orcid_id=cached["orcid_id"],
                name=cached["name"],
                affiliations=cached["affiliations"],
                works=[OrcidWork(**w) for w in cached["works"]],
            )

        data = self._get(f"{BASE_URL}/{orcid_id}/record")
        if not data:
            return None

        person = data.get("person", {})
        name_data = person.get("name", {})
        given = (name_data.get("given-names") or {}).get("value", "")
        family = (name_data.get("family-name") or {}).get("value", "")
        full_name = f"{given} {family}".strip()

        affiliations = []
        activities = data.get("activities-summary", {})
        for emp in (activities.get("employments", {}).get("affiliation-group", []) or []):
            summaries = emp.get("summaries", [])
            for s in summaries:
                es = s.get("employment-summary", {})
                org = es.get("organization", {})
                org_name = org.get("name", "")
                dept = es.get("department-name", "")
                if org_name:
                    entry = f"{dept}, {org_name}" if dept else org_name
                    if entry not in affiliations:
                        affiliations.append(entry)

        works = self._extract_works(data)

        profile = OrcidProfile(
            orcid_id=orcid_id,
            name=full_name,
            affiliations=affiliations,
            works=works,
        )
        cache.put("orcid", cache_key, {
            "orcid_id": profile.orcid_id,
            "name": profile.name,
            "affiliations": profile.affiliations,
            "works": [{"title": w.title, "year": w.year, "doi": w.doi, "work_type": w.work_type} for w in profile.works],
        })
        return profile

    def _extract_works(self, record_data: dict[str, Any]) -> list[OrcidWork]:
        """Extrai os trabalhos publicados do registro ORCID."""
        activities = record_data.get("activities-summary", {})
        work_groups = activities.get("works", {}).get("group", []) or []

        works: list[OrcidWork] = []
        for group in work_groups[:20]:
            summaries = group.get("work-summary", [])
            if not summaries:
                continue
            ws = summaries[0]

            title_data = ws.get("title", {})
            title_val = (title_data.get("title") or {}).get("value", "")

            year = None
            pub_date = ws.get("publication-date") or {}
            year_data = pub_date.get("year")
            if year_data and year_data.get("value"):
                try:
                    year = int(year_data["value"])
                except (ValueError, TypeError):
                    pass

            doi = None
            ext_ids = group.get("external-ids", {}).get("external-id", []) or []
            for eid in ext_ids:
                if eid.get("external-id-type") == "doi":
                    doi = eid.get("external-id-value")
                    break

            work_type = ws.get("type")

            if title_val:
                works.append(OrcidWork(title=title_val, year=year, doi=doi, work_type=work_type))

        works.sort(key=lambda w: (w.year or 0), reverse=True)
        return works

    def find_professor(self, name: str, affiliation: str) -> OrcidProfile | None:
        """
        Fluxo completo: busca o professor por nome + afiliação, retorna o perfil
        mais provável ou None se não encontrar.
        """
        candidates = self.search_by_name_and_affiliation(name, affiliation)
        if not candidates:
            return None

        aff_lower = affiliation.lower()
        best = None
        best_score = -1

        for c in candidates:
            orcid_id = c.get("orcid-id", "")
            institutions = c.get("institution-name", []) or []
            score = 0
            for inst in institutions:
                if aff_lower in inst.lower():
                    score = 2
                    break
                elif any(word in inst.lower() for word in aff_lower.split()):
                    score = max(score, 1)
            if score > best_score:
                best_score = score
                best = orcid_id

        if not best:
            best = candidates[0].get("orcid-id", "")

        if not best:
            return None

        return self.get_profile(best)


def format_orcid_profile(profile: OrcidProfile, enriched_works: list[dict[str, Any]] | None = None) -> str:
    """Formata um perfil ORCID em Markdown para o relatório."""
    lines = [
        f"### {profile.name}",
        f"- ORCID: https://orcid.org/{profile.orcid_id}",
        f"- Afiliações: {'; '.join(profile.affiliations[:3]) or 'N/D'}",
        "",
    ]

    if enriched_works:
        lines.append("**Publicações recentes (via ORCID + Semantic Scholar):**")
        for w in enriched_works[:5]:
            year = w.get("year", "s/d")
            title = w.get("title", "sem título")
            venue = w.get("venue", "")
            cites = w.get("citationCount", "?")
            venue_str = f" — {venue}" if venue else ""
            lines.append(f"  - ({year}) {title}{venue_str} — {cites} citações")
    elif profile.works:
        lines.append("**Publicações recentes (ORCID, sem dados de citação):**")
        for w in profile.works[:5]:
            year = w.year or "s/d"
            doi_str = f" [DOI: {w.doi}]" if w.doi else ""
            lines.append(f"  - ({year}) {w.title}{doi_str}")
    else:
        lines.append("_Nenhum trabalho registrado no ORCID._")

    return "\n".join(lines)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, stream=__import__("sys").stderr)
    logger = logging.getLogger(__name__)
    client = OrcidClient()
    profile = client.find_professor("Samir Khuller", "Northwestern University")
    if profile:
        logger.info("Found: %s (%s)", profile.name, profile.orcid_id)
        logger.info("Affiliations: %s", profile.affiliations)
        logger.info("Works: %d", len(profile.works))
        for w in profile.works[:5]:
            logger.info("  - (%s) %s [DOI: %s]", w.year, w.title, w.doi)
    else:
        logger.info("Not found.")
