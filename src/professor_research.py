"""
Unified professor research: cascades through 4 data sources.

Fallback order (each raises confidence when it matches; first non-empty wins):
  1. ORCID — desambiguação por afiliação institucional. Cobertura fraca para
     cientistas seniores de CS que não mantêm ORCID.
  2. DBLP — bibliografia canônica de CS. Cobertura excelente de CS/ECE, inclui
     afiliação nas hits de busca. Sem citações/h-index.
  3. OpenAlex — cobertura ampla, disambiguação por instituição, tem h-index e
     works_count. Cobre áreas fora de CS.
  4. Semantic Scholar — última tentativa; busca por nome sem confirmação forte
     de afiliação, então é always low-confidence.

O resultado retorna proveniência e confiança explícitas — o formatador do
relatório deve mostrar ambos para o usuário saber em que confiar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .dblp_client import DblpClient
from .openalex_client import OpenAlexClient
from .orcid_client import OrcidClient
from .semantic_scholar import SemanticScholarClient


@dataclass
class Publication:
    title: str
    year: int | None
    venue: str | None = None
    doi: str | None = None
    citation_count: int | None = None  # None = not reported by this source


@dataclass
class ResearchResult:
    professor_name: str
    identified_as: str  # canonical name as reported by the source
    source: str  # 'orcid' | 'dblp' | 'openalex' | 'semantic_scholar' | 'none'
    confidence: str  # 'high' | 'medium' | 'low' | 'none'
    profile_url: str | None
    affiliation: str | None
    publications: list[Publication] = field(default_factory=list)
    h_index: int | None = None
    total_works: int | None = None
    # Warning displayed to user when confidence < high
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "professor_name": self.professor_name,
            "identified_as": self.identified_as,
            "source": self.source,
            "identification_confidence": self.confidence,
            "profile_url": self.profile_url,
            "affiliation": self.affiliation,
            "publications": [
                {
                    "title": p.title, "year": p.year, "venue": p.venue,
                    "doi": p.doi, "citation_count": p.citation_count,
                }
                for p in self.publications
            ],
            "h_index": self.h_index,
            "total_works": self.total_works,
            "warning": self.warning,
        }

    def scoring_text(self) -> str:
        """Concatenated text for interest-matching scoring."""
        parts = [self.identified_as, self.affiliation or ""]
        for p in self.publications:
            parts.append(p.title or "")
            parts.append(p.venue or "")
        return " ".join(parts)

    @classmethod
    def empty(cls, professor_name: str) -> "ResearchResult":
        return cls(
            professor_name=professor_name,
            identified_as=professor_name,
            source="none",
            confidence="none",
            profile_url=None,
            affiliation=None,
        )


def _try_orcid(
    name: str, affiliation: str, orcid: OrcidClient, ss: SemanticScholarClient,
) -> ResearchResult | None:
    profile = orcid.find_professor(name, affiliation)
    if not profile:
        return None

    # Validate affiliation match — prevents false positives from homonyms
    aff_lower = affiliation.lower()
    aff_words = set(aff_lower.split())
    profile_affs_text = " ".join(profile.affiliations).lower()
    if aff_lower in profile_affs_text:
        confidence = "high"
        warning = None
    elif aff_words & set(profile_affs_text.split()):
        confidence = "medium"
        warning = (
            f"ORCID profile found but affiliation doesn't exactly match "
            f"'{affiliation}'. Listed affiliations: {'; '.join(profile.affiliations[:3])}. "
            "May be a homonym — verify manually."
        )
    else:
        confidence = "low"
        warning = (
            f"ORCID returned a result for '{name}' but affiliations "
            f"({'; '.join(profile.affiliations[:3]) or 'none listed'}) do NOT match "
            f"'{affiliation}'. Likely a different person. DO NOT USE without verification."
        )

    pubs: list[Publication] = []
    for work in profile.works[:8]:
        pub = Publication(title=work.title, year=work.year, doi=work.doi)
        if work.doi:
            try:
                paper = ss.get_paper_by_doi(work.doi)
                if paper:
                    pub.venue = paper.get("venue") or None
                    pub.citation_count = paper.get("citationCount")
            except Exception:
                pass
        pubs.append(pub)
    return ResearchResult(
        professor_name=name,
        identified_as=profile.name or name,
        source="orcid",
        confidence=confidence,
        profile_url=f"https://orcid.org/{profile.orcid_id}",
        affiliation="; ".join(profile.affiliations[:3]) or None,
        publications=pubs,
        h_index=None,
        total_works=len(profile.works),
        warning=warning,
    )


def _try_dblp(name: str, affiliation: str, dblp: DblpClient) -> ResearchResult | None:
    found = dblp.find_professor(name, affiliation)
    if not found:
        return None
    author, conf = found
    pubs_raw = dblp.get_publications(author.pid, limit=8)
    pubs = [
        Publication(title=p.title, year=p.year, venue=p.venue)
        for p in pubs_raw
    ]
    warning = None
    if conf != "high":
        warning = (
            f"DBLP found a match but couldn't confirm affiliation with "
            f"'{affiliation}'. Verify manually."
        )
    return ResearchResult(
        professor_name=name,
        identified_as=author.name,
        source="dblp",
        confidence=conf,
        profile_url=author.url,
        affiliation=author.affiliation,
        publications=pubs,
        h_index=None,
        total_works=None,
        warning=warning,
    )


def _try_openalex(name: str, affiliation: str, oa: OpenAlexClient) -> ResearchResult | None:
    found = oa.find_professor(name, affiliation)
    if not found:
        return None
    author, conf = found
    pubs_raw = oa.get_publications(author.author_id, limit=8)
    pubs = [
        Publication(
            title=p.title, year=p.year, venue=p.venue, doi=p.doi,
            citation_count=p.cited_by_count,
        )
        for p in pubs_raw
    ]
    warning = None
    if conf != "high":
        warning = (
            f"OpenAlex found a match but couldn't confirm the institution as "
            f"'{affiliation}' (found: {', '.join(author.institutions) or 'none listed'}). "
            "Verify manually."
        )
    return ResearchResult(
        professor_name=name,
        identified_as=author.name,
        source="openalex",
        confidence=conf,
        profile_url=author.author_id,
        affiliation=", ".join(author.institutions) or None,
        publications=pubs,
        h_index=author.h_index,
        total_works=author.works_count,
        warning=warning,
    )


def _try_semantic_scholar(
    name: str, affiliation: str, ss: SemanticScholarClient,
) -> ResearchResult | None:
    try:
        r = ss.find_professor_research(name, affiliation_hint=affiliation)
    except RuntimeError:
        return None
    if not r:
        return None
    pubs_raw = r.get("recent_papers") or []
    pubs = [
        Publication(
            title=p.get("title", ""), year=p.get("year"),
            venue=p.get("venue"), citation_count=p.get("citationCount"),
        )
        for p in pubs_raw if p.get("title")
    ]
    return ResearchResult(
        professor_name=name,
        identified_as=r.get("name") or name,
        source="semantic_scholar",
        confidence="low",
        profile_url=r.get("profile_url"),
        affiliation=", ".join(r.get("affiliations") or []) or None,
        publications=pubs,
        h_index=r.get("h_index"),
        total_works=r.get("paper_count"),
        warning=(
            "Identified via name search only — no strong affiliation match. "
            "May be a different person with the same name. Verify manually."
        ),
    )


def research_professor(
    name: str,
    university_name: str,
    orcid: OrcidClient | None = None,
    dblp: DblpClient | None = None,
    openalex: OpenAlexClient | None = None,
    ss: SemanticScholarClient | None = None,
    profile_hint_orcid_id: str | None = None,
) -> ResearchResult:
    """
    Run the ORCID → DBLP → OpenAlex → Semantic Scholar fallback chain.
    Returns the first non-empty result, or ResearchResult.empty() if all miss.

    `profile_hint_orcid_id` bypasses ORCID search when the faculty profile
    page already exposed the professor's ORCID.
    """
    orcid = orcid or OrcidClient()
    dblp = dblp or DblpClient()
    openalex = openalex or OpenAlexClient()
    ss = ss or SemanticScholarClient()

    # If we already have an ORCID id (from profile page scrape), fetch directly
    if profile_hint_orcid_id:
        profile = orcid.get_profile(profile_hint_orcid_id)
        if profile and profile.works:
            pubs: list[Publication] = []
            for work in profile.works[:8]:
                pub = Publication(title=work.title, year=work.year, doi=work.doi)
                if work.doi:
                    try:
                        paper = ss.get_paper_by_doi(work.doi)
                        if paper:
                            pub.venue = paper.get("venue") or None
                            pub.citation_count = paper.get("citationCount")
                    except Exception:
                        pass
                pubs.append(pub)
            return ResearchResult(
                professor_name=name,
                identified_as=profile.name or name,
                source="orcid",
                confidence="high",
                profile_url=f"https://orcid.org/{profile.orcid_id}",
                affiliation="; ".join(profile.affiliations[:3]) or None,
                publications=pubs,
                total_works=len(profile.works),
            )

    for fn in (
        lambda: _try_orcid(name, university_name, orcid, ss),
        lambda: _try_dblp(name, university_name, dblp),
        lambda: _try_openalex(name, university_name, openalex),
        lambda: _try_semantic_scholar(name, university_name, ss),
    ):
        result = fn()
        if result and result.publications:
            return result

    return ResearchResult.empty(name)


def format_research_result_md(r: ResearchResult) -> str:
    """Format a ResearchResult as a Markdown block for the report."""
    if r.source == "none":
        return (
            f"### {r.professor_name}\n"
            "_Sem publicações encontradas em ORCID, DBLP, OpenAlex ou "
            "Semantic Scholar. Isso NÃO significa que o professor não pesquisa "
            "— consulte a página oficial dele no departamento._"
        )

    src_label = {
        "orcid": "ORCID",
        "dblp": "DBLP",
        "openalex": "OpenAlex",
        "semantic_scholar": "Semantic Scholar",
    }.get(r.source, r.source)

    conf_marker = {
        "high": "✅",
        "medium": "⚠️",
        "low": "⚠️",
    }.get(r.confidence, "")

    lines = [
        f"### {r.identified_as}",
        f"- Fonte: {src_label} {conf_marker} confiança={r.confidence}",
    ]
    if r.profile_url:
        lines.append(f"- Perfil: {r.profile_url}")
    if r.affiliation:
        lines.append(f"- Afiliação (reportada pela fonte): {r.affiliation}")
    if r.h_index is not None:
        h_context = "" if r.total_works is None else f" ({r.total_works} trabalhos)"
        lines.append(f"- h-index: {r.h_index}{h_context}")
    elif r.total_works is not None:
        lines.append(f"- Trabalhos indexados: {r.total_works}")

    if r.warning:
        lines.append(f"- ⚠️ {r.warning}")

    if r.publications:
        lines.append("")
        lines.append("**Publicações recentes:**")
        for p in r.publications[:5]:
            year = p.year if p.year is not None else "s/d"
            venue = f" — {p.venue}" if p.venue else ""
            cites = ""
            if p.citation_count is not None:
                cites = f" — {p.citation_count} citações"
            lines.append(f"  - ({year}) {p.title}{venue}{cites}")

    return "\n".join(lines)
