"""
Scraper genérico e configurável de diretórios de faculty (corpo docente).

Diferente do College Scorecard e Semantic Scholar, não existe uma API única
para "lista de professores de qualquer universidade" — cada universidade tem
seu próprio site institucional. Este módulo resolve isso com um sistema de
CONFIGURAÇÃO por universidade (seletores CSS), em vez de um scraper hardcoded
para uma escola só.

Extração em duas camadas:
  1) Listagem: nome, título, link do perfil, e-mail (opcional). Baseado em
     seletores CSS do bloco "selectors" no faculty_configs.json.
  2) Página de perfil individual (opcional, `fetch_profiles=True`): bio,
     research_areas, lab_url, orcid_id. Usa heurística por texto de heading
     (h2/h3/h4) com override via bloco "profile_selectors" do config.

Boas práticas aplicadas:
- Respeita robots.txt antes de fazer scraping.
- Delay entre requests (não sobrecarrega o servidor da universidade).
- Cache SQLite agressivo por URL de perfil (TTL 30 dias) para evitar re-scrape.
- Só extrai dados institucionais públicos (nome, cargo, área, e-mail
  profissional, link do perfil) — nunca dados pessoais sensíveis.

Para adicionar uma nova universidade: inspecione o HTML da página de faculty
do departamento (botão direito > Inspecionar no navegador) e preencha um novo
bloco em data/faculty_configs.json seguindo o modelo dos exemplos.
"""

from __future__ import annotations

import json
import re
import time
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from . import cache
from .source_tracker import record_source

CONFIG_PATH = Path(__file__).parent.parent / "data" / "faculty_configs.json"

# Role type is inferred from title text + URL structure.
# The URL structure matters because "(by courtesy)" in a title indicates a
# SECONDARY courtesy appointment, not a primary one. Ex: Peter Dinda is
# "Professor of Computer Science and (by courtesy) ECE" — his primary is CS,
# and his profile lives under /profiles/. Nabil Alshurafa is
# "Associate Professor of Preventive Medicine and (by courtesy) CS" — primary
# is outside CS, and his profile lives under /affiliated/. Only the URL tells
# us which of the two situations we're in.

_TEACHING_TITLE_KEYWORDS = [
    "professor of instruction", "professor of practice", "clinical professor",
    "senior lecturer", "lecturer", "instructor",
]

# Common heading labels on faculty profile pages. Case-insensitive match.
PROFILE_HEADING_ALIASES: dict[str, list[str]] = {
    "bio": ["research interests", "research areas", "research", "bio", "biography",
            "about", "overview", "profile"],
    "lab_url": ["website", "websites", "personal website", "lab", "laboratory",
                "group", "homepage", "personal page"],
    "departments": ["departments", "department", "affiliations", "appointments"],
}

ORCID_URL_RE = re.compile(r"https?://(?:sandbox\.)?orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])",
                          re.IGNORECASE)


@dataclass
class FacultyMember:
    name: str
    title: str | None
    research_areas: str | None
    email: str | None
    profile_url: str | None
    # Enriched via profile page fetch (only present when fetch_profiles=True)
    bio: str | None = None
    lab_url: str | None = None
    orcid_id: str | None = None
    role_type: str = "unknown"
    departments_list: list[str] = field(default_factory=list)

    def limited_undergrad_advising(self) -> bool:
        """
        Heuristic: adjunct, emeritus, and affiliated (courtesy) appointments
        typically indicate limited or no capacity to advise undergraduates as
        primary advisors. Teaching-focused roles CAN advise undergrads and
        should not be flagged. Instruction-only roles (lecturer/instructor)
        usually don't lead research groups.
        """
        return self.role_type in {"adjunct", "emeritus", "affiliated"}


def _robots_allowed(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        # Se não conseguir ler o robots.txt, segue com cautela (assume permitido)
        # mas isso é raro — normalmente indica que o site está fora do ar.
        return True


def load_configs() -> dict[str, Any]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _classify_role_type(title: str | None, profile_url: str | None = None) -> str:
    """
    Classify a faculty member's appointment relative to the department being
    scraped. Uses both the title and the profile URL (some universities
    separate primary vs. courtesy appointments by URL path — e.g. Northwestern
    uses /directory/profiles/ vs. /directory/affiliated/).
    """
    url_lower = (profile_url or "").lower()
    url_signals_affiliated = "/affiliated/" in url_lower

    if not title:
        return "affiliated" if url_signals_affiliated else "unknown"

    t = title.lower()

    # Highest-priority signals: title starts with adjunct / contains emeritus.
    if "emeritus" in t or "emerita" in t:
        return "emeritus"
    if t.startswith("adjunct"):
        return "adjunct"

    # Teaching-focused explicit titles.
    for kw in _TEACHING_TITLE_KEYWORDS:
        if kw in t:
            return "teaching"

    # If the URL path says /affiliated/, trust it — this is the department's
    # own classification, and it correctly handles "(by courtesy)" secondary
    # appointments without misclassifying primary tenure-track faculty.
    if url_signals_affiliated:
        return "affiliated"

    # Fallback: any "professor" title without the above signals is tenure-track.
    if "professor" in t or "endowed" in t or "chair" in t:
        return "tenure_track"

    return "unknown"


def _fetch_page(url: str, user_agent: str, delay_seconds: float) -> str | None:
    """Fetch a URL with error handling. Returns HTML text or None on failure."""
    try:
        resp = requests.get(url, headers={"User-Agent": user_agent}, timeout=20)
        resp.raise_for_status()
    except (requests.Timeout, requests.HTTPError, requests.ConnectionError):
        return None
    time.sleep(delay_seconds)
    return resp.text


def _extract_next_siblings_text(heading_tag) -> str:
    """From a heading tag, collect text from following siblings until the next
    heading of the same or higher level. Preserves line breaks between blocks."""
    parts: list[str] = []
    cur = heading_tag.next_sibling
    stop_levels = {"h1", "h2", "h3", "h4", "h5", "h6"}
    while cur is not None:
        name = getattr(cur, "name", None)
        if name in stop_levels:
            break
        get_text = getattr(cur, "get_text", None)
        if callable(get_text):
            txt = get_text(" ", strip=True).replace("\xa0", " ")
            if txt:
                parts.append(txt)
        cur = cur.next_sibling
    return "\n".join(parts).strip()


def _extract_first_link(heading_tag, base_url: str) -> str | None:
    """From a heading tag, return the href of the first <a> in the following
    siblings up to the next heading."""
    cur = heading_tag.next_sibling
    stop_levels = {"h1", "h2", "h3", "h4", "h5", "h6"}
    while cur is not None:
        name = getattr(cur, "name", None)
        if name in stop_levels:
            break
        find_a = getattr(cur, "find", None)
        if callable(find_a):
            a = cur.find("a", href=True) if name else None
            if a and a.get("href"):
                return urljoin(base_url, a["href"])
            if name == "a" and cur.get("href"):
                return urljoin(base_url, cur["href"])
        cur = cur.next_sibling
    return None


def _extract_profile_data(
    html: str,
    profile_url: str,
    profile_selectors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Extract enrichment fields from a professor's profile page HTML.

    Heuristic first (heading text match), overridden by explicit CSS selectors
    if provided in profile_selectors.
    """
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, Any] = {
        "bio": None,
        "lab_url": None,
        "orcid_id": None,
        "departments_list": [],
    }

    # --- Heuristic pass by heading text ---
    heading_index: dict[str, list] = {}  # normalized_label -> list of heading tags
    for h in soup.find_all(["h2", "h3", "h4", "h5"]):
        label = h.get_text(strip=True).lower().replace("\xa0", " ").strip(": ")
        heading_index.setdefault(label, []).append(h)

    def _find_heading(field_key: str):
        for alias in PROFILE_HEADING_ALIASES.get(field_key, []):
            tags = heading_index.get(alias)
            if tags:
                return tags[0]
        return None

    bio_h = _find_heading("bio")
    if bio_h:
        result["bio"] = _extract_next_siblings_text(bio_h) or None

    lab_h = _find_heading("lab_url")
    if lab_h:
        result["lab_url"] = _extract_first_link(lab_h, profile_url)

    dept_h = _find_heading("departments")
    if dept_h:
        dept_text = _extract_next_siblings_text(dept_h)
        # Split by newline or common separators
        depts = []
        for line in dept_text.split("\n"):
            line = line.strip()
            if not line or line.lower().startswith("download"):
                continue
            # Skip if it looks like a link label (contains phone/email/etc)
            if any(kw in line.lower() for kw in ["download cv", "email", "phone"]):
                continue
            depts.append(line)
        result["departments_list"] = depts

    # --- CSS selector overrides ---
    if profile_selectors:
        for field_name, sel in profile_selectors.items():
            if not sel or field_name not in ("bio", "lab_url", "departments"):
                continue
            el = soup.select_one(sel) if isinstance(sel, str) else None
            if not el:
                continue
            if field_name == "bio":
                result["bio"] = el.get_text(" ", strip=True).replace("\xa0", " ") or None
            elif field_name == "lab_url":
                if el.name == "a" and el.get("href"):
                    result["lab_url"] = urljoin(profile_url, el["href"])
                else:
                    a = el.find("a", href=True)
                    if a:
                        result["lab_url"] = urljoin(profile_url, a["href"])
            elif field_name == "departments":
                text = el.get_text("\n", strip=True).replace("\xa0", " ")
                result["departments_list"] = [
                    ln.strip() for ln in text.split("\n") if ln.strip()
                ]

    # --- ORCID: scan any anchor on the page for orcid.org URLs ---
    for a in soup.find_all("a", href=True):
        m = ORCID_URL_RE.search(a["href"])
        if m:
            result["orcid_id"] = m.group(1)
            break
    if not result["orcid_id"]:
        # Also try in plain text (some pages list "ORCID: 0000-...")
        page_text = soup.get_text(" ", strip=True)
        m = re.search(r"\b(\d{4}-\d{4}-\d{4}-\d{3}[\dX])\b", page_text)
        if m:
            result["orcid_id"] = m.group(1)

    return result


def _enrich_from_profile(
    member: FacultyMember,
    profile_selectors: dict[str, Any] | None,
    user_agent: str,
    delay_seconds: float,
) -> FacultyMember:
    """Fetch member.profile_url and merge extracted fields into member."""
    if not member.profile_url:
        return member

    cache_key = f"profile:{member.profile_url}"
    cached = cache.get("faculty_profile", cache_key, max_age_days=30)
    if cached is None:
        html = _fetch_page(member.profile_url, user_agent, delay_seconds)
        if html is None:
            # Fetch failed — leave member as-is, but do NOT cache the failure
            return member
        # Track the profile page
        record_source(
            url=member.profile_url,
            title=f"Faculty Profile - {member.name}",
            university=None,  # Will be inferred from domain
            category="faculty"
        )
        cached = _extract_profile_data(html, member.profile_url, profile_selectors)
        cache.put("faculty_profile", cache_key, cached)

    if cached.get("bio"):
        member.bio = cached["bio"]
        # Populate research_areas from bio if the listing page didn't have one.
        # The bio contains the research description on many pages (like Northwestern).
        if not member.research_areas:
            # Take first 400 chars as a research summary — full bio available
            # separately in member.bio.
            member.research_areas = cached["bio"][:400].rstrip()
    if cached.get("lab_url"):
        member.lab_url = cached["lab_url"]
    if cached.get("orcid_id"):
        member.orcid_id = cached["orcid_id"]
    if cached.get("departments_list"):
        member.departments_list = cached["departments_list"]

    return member


def scrape_faculty(
    university_key: str,
    delay_seconds: float = 1.0,
    fetch_profiles: bool = False,
    profile_limit: int | None = None,
) -> list[FacultyMember]:
    """
    Faz scraping da página de faculty de uma universidade configurada em
    data/faculty_configs.json.

    Args:
        university_key: chave em faculty_configs.json (ex: "northwestern_cs").
        delay_seconds: delay entre requests (respeito ao servidor).
        fetch_profiles: se True, visita cada profile_url e enriquece com
            bio, research_areas (se ausente), lab_url, orcid_id. Multiplica
            requests, mas o cache SQLite por URL é agressivo (30 dias).
        profile_limit: se fornecido junto com fetch_profiles, limita o
            enriquecimento aos primeiros N professores (útil pra teste rápido).
    """
    configs = load_configs()
    if university_key not in configs:
        raise KeyError(
            f"'{university_key}' não está configurado. "
            f"Universidades disponíveis: {list(configs.keys())}. "
            f"Adicione uma nova config em data/faculty_configs.json."
        )

    cfg = configs[university_key]
    url = cfg["url"]
    user_agent = "college-research-tool/1.0"

    if not _robots_allowed(url):
        raise PermissionError(f"robots.txt não permite scraping de {url}")

    html = _fetch_page(url, user_agent, delay_seconds)
    if html is None:
        raise RuntimeError(f"Faculty scraper: falha ao acessar {url}")

    # Track the faculty listing page
    university_name = cfg.get("university", university_key)
    record_source(
        url=url,
        title=f"Faculty Directory - {university_name}",
        university=university_name,
        category="faculty"
    )

    soup = BeautifulSoup(html, "html.parser")
    members: list[FacultyMember] = []

    def _select(card, key):
        sel = cfg["selectors"].get(key, "")
        return card.select_one(sel) if sel else None

    for card in soup.select(cfg["selectors"]["card"]):
        name_el = _select(card, "name")
        title_el = _select(card, "title")
        research_el = _select(card, "research_areas")
        email_el = _select(card, "email")
        link_el = _select(card, "profile_link")

        profile_url = None
        if link_el and link_el.get("href"):
            profile_url = urljoin(url, link_el["href"])

        email = None
        if email_el:
            email = email_el.get_text(strip=True) or email_el.get("href", "").replace("mailto:", "")

        if name_el:
            title_text = title_el.get_text(strip=True).replace("\xa0", " ") if title_el else None
            members.append(
                FacultyMember(
                    name=name_el.get_text(strip=True).replace("\xa0", " "),
                    title=title_text,
                    research_areas=research_el.get_text(strip=True).replace("\xa0", " ") if research_el else None,
                    email=email,
                    profile_url=profile_url,
                    role_type=_classify_role_type(title_text, profile_url),
                )
            )

    if fetch_profiles:
        profile_selectors = cfg.get("profile_selectors")
        targets = members if profile_limit is None else members[:profile_limit]
        for m in targets:
            _enrich_from_profile(m, profile_selectors, user_agent, delay_seconds)

    return members


def format_faculty_list(members: list[FacultyMember]) -> str:
    if not members:
        return "Nenhum professor encontrado (revise os seletores da config)."
    lines = ["| Nome | Cargo | Vínculo | Área de pesquisa | Perfil |",
             "|---|---|---|---|---|"]
    for m in members:
        role_display = m.role_type
        if m.limited_undergrad_advising():
            role_display = f"⚠️ {m.role_type}"
        area = (m.research_areas or "N/D")
        if len(area) > 120:
            area = area[:117] + "..."
        lines.append(
            f"| {m.name} | {m.title or 'N/D'} | {role_display} | {area} | "
            f"{m.profile_url or 'N/D'} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    key = sys.argv[1] if len(sys.argv) > 1 else "example_university_cs_dept"
    fetch = "--fetch-profiles" in sys.argv
    limit = None
    for a in sys.argv:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
    try:
        faculty = scrape_faculty(key, fetch_profiles=fetch, profile_limit=limit)
        logging.info(format_faculty_list(faculty))
        # Also dump enrichment stats
        with_area = sum(1 for m in faculty if m.research_areas)
        with_lab = sum(1 for m in faculty if m.lab_url)
        with_orcid = sum(1 for m in faculty if m.orcid_id)
        logging.info(
            "Enrichment: %d total, %d with research_areas, %d with lab_url, %d with orcid",
            len(faculty), with_area, with_lab, with_orcid,
        )
    except KeyError as e:
        logging.error(str(e))
