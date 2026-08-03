"""
Orquestrador: junta College Scorecard + ORCID + Semantic Scholar + Faculty Scraper +
Alumni Research em um único relatório Markdown por universidade.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Callable

from .alumni_research import find_linkedin_slug_hint, format_alumni_links, generate_alumni_queries
from .career_outcomes import format_career_outcomes, get_university_career_outcomes
from .college_scorecard import CollegeScorecardClient, format_school_summary
from .dblp_client import DblpClient
from .faculty_scraper import FacultyMember, format_faculty_list, scrape_faculty
from .openalex_client import OpenAlexClient
from .orcid_client import OrcidClient
from .professor_research import format_research_result_md, research_professor
from .semantic_scholar import SemanticScholarClient
from .student_profile import StudentProfile, compute_relevance_score
from .university_opportunities import format_opportunities, get_university_opportunities

OUTPUT_DIR = Path(__file__).parent.parent / "output"

STAR_THRESHOLD = 0.4


def research_university(
    university_name: str,
    faculty_config_key: str | None = None,
    field_of_interest: str | None = None,
    max_professors_for_research: int = 5,
    student_profile: StudentProfile | None = None,
    fetch_faculty_profiles: bool = True,
    on_progress: Callable[[str], None] | None = None,
) -> str:
    """
    Gera o relatório completo de uma universidade.

    Fluxo de pesquisa acadêmica por professor:
      1. ORCID (fonte de verdade — desambigua por afiliação institucional)
      2. Se não achar no ORCID, fallback para Semantic Scholar author search
      3. Se nenhum achar, mostra "não encontrado"

    Se student_profile for passado, ordena professores por relevância.
    """
    def _progress(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    report_parts = [f"# Relatório: {university_name}", f"_Gerado em {date.today().isoformat()}_", ""]

    if student_profile and student_profile.interests:
        report_parts.append(f"**Perfil do aluno:** interesses = {', '.join(student_profile.interests)} | "
                            f"objetivo = {student_profile.goal}")
        report_parts.append("")

    # 1. Dados oficiais (College Scorecard)
    _progress("Buscando dados na College Scorecard...")
    report_parts.append("## 1. Dados gerais (College Scorecard)")
    try:
        sc_client = CollegeScorecardClient()
        school = sc_client.get_by_exact_name(university_name)
        report_parts.append(format_school_summary(school) if school else "Não encontrado na College Scorecard API.")
    except (ValueError, RuntimeError) as e:
        report_parts.append(f"_Pulado: {e}_")
    report_parts.append("")

    # 2. Faculty
    _progress("Scraping corpo docente...")
    faculty_members: list[FacultyMember] = []
    report_parts.append("## 2. Corpo docente")
    if faculty_config_key:
        try:
            faculty_members = scrape_faculty(
                faculty_config_key, fetch_profiles=fetch_faculty_profiles,
            )
            report_parts.append(format_faculty_list(faculty_members))
        except (KeyError, PermissionError, RuntimeError) as e:
            report_parts.append(f"_Erro: {e}_")
    else:
        report_parts.append("_Nenhuma config de faculty informada — pulei essa seção. "
                             "Veja data/faculty_configs.json para adicionar uma._")
    report_parts.append("")

    # 3. Pesquisa acadêmica: cadeia de fallback ORCID -> DBLP -> OpenAlex -> Semantic Scholar
    _progress("Pesquisando perfis acadêmicos (ORCID + DBLP + OpenAlex + SS)...")
    report_parts.append("## 3. Pesquisa acadêmica dos professores")
    if student_profile and student_profile.interests:
        report_parts.append(f"_Ordenado por relevância para: {', '.join(student_profile.interests)}_\n")
    report_parts.append(
        "_Cadeia de fontes: **ORCID** (desambiguação por afiliação) → "
        "**DBLP** (canônica de CS) → **OpenAlex** (ampla, com h-index) → "
        "**Semantic Scholar** (busca por nome, baixa confiança)._\n"
    )

    if faculty_members:
        orcid_client = OrcidClient()
        ss_client = SemanticScholarClient()
        dblp_client = DblpClient()
        oa_client = OpenAlexClient()

        professor_results: list[tuple[float, str, str]] = []

        for i, member in enumerate(faculty_members[:max_professors_for_research], 1):
            _progress(f"  Professor {i}/{min(len(faculty_members), max_professors_for_research)}: {member.name}")
            result = research_professor(
                member.name, university_name,
                orcid=orcid_client, dblp=dblp_client,
                openalex=oa_client, ss=ss_client,
                profile_hint_orcid_id=member.orcid_id,
            )

            md = format_research_result_md(result)
            # Include title, role, research_areas (from profile page) and pubs in scoring text
            scoring_text_parts = [
                member.title or "",
                member.role_type or "",
                member.research_areas or "",
                result.scoring_text(),
            ]
            scoring_text = " ".join(scoring_text_parts)

            score = 0.0
            if student_profile:
                score = compute_relevance_score(scoring_text, student_profile)

            # If role has limited undergrad availability, note it inline
            if member.limited_undergrad_advising():
                md = (
                    f"_⚠️ Vínculo `{member.role_type}` — normalmente com "
                    "disponibilidade limitada para orientar undergrad como advisor primário._\n\n"
                    + md
                )

            professor_results.append((score, md, member.name))

        if student_profile and student_profile.interests:
            professor_results.sort(key=lambda x: x[0], reverse=True)

        for score, md, name in professor_results:
            if student_profile and student_profile.interests and score >= STAR_THRESHOLD:
                report_parts.append(f"⭐ **Alta relevância (score: {score:.2f})**\n")
            elif student_profile and student_profile.interests and score > 0:
                report_parts.append(f"_Relevância: {score:.2f}_\n")
            report_parts.append(md)
            report_parts.append("")
    else:
        report_parts.append("_Sem lista de professores para cruzar — preencha a seção 2 primeiro._")
    report_parts.append("")

    # 4. Oportunidades
    _progress("Carregando oportunidades...")
    report_parts.append("## 4. Oportunidades na universidade")
    opps = get_university_opportunities(university_name)
    if opps:
        report_parts.append(format_opportunities(opps))
    else:
        report_parts.append("_Nenhuma oportunidade configurada para esta universidade. "
                            "Adicione um bloco em data/opportunities.json._")
    report_parts.append("")

    # 5. Alumni
    _progress("Montando seção de alumni e career outcomes...")
    report_parts.append("## 5. Trajetória de alumni")

    # 5a. Career outcomes (dados agregados do relatório oficial)
    career_data = get_university_career_outcomes(university_name)
    if career_data:
        report_parts.append(format_career_outcomes(career_data))
    else:
        report_parts.append("_Nenhum relatório de career outcomes configurado para esta universidade. "
                            "Adicione um bloco em data/career_outcomes.json._\n")

    # 5b. Links para pesquisa manual no LinkedIn Alumni Tool
    report_parts.append("### Links de pesquisa (LinkedIn Alumni Tool)")
    slug = find_linkedin_slug_hint(university_name)
    queries = generate_alumni_queries(slug, field_of_study=field_of_interest)
    report_parts.append(format_alumni_links(queries))

    return "\n".join(report_parts)


def save_report(university_name: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = university_name.lower().replace(" ", "_").replace(",", "") + ".md"
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path
