"""
Módulo de career outcomes — dados agregados de relatórios oficiais de pós-graduação.

Lê dados curados de data/career_outcomes.json (extraídos manualmente de PDFs/páginas
publicadas pelas universidades). Sem scraping de perfis individuais.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CAREER_DATA_PATH = Path(__file__).parent.parent / "data" / "career_outcomes.json"


def load_career_data() -> dict[str, Any]:
    with open(CAREER_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_university_career_outcomes(university_name: str) -> dict[str, Any] | None:
    """Retorna os dados de career outcomes de uma universidade ou None."""
    data = load_career_data()
    key = university_name.strip().lower().replace(" ", "_").replace(",", "")
    return data.get(key)


def format_career_outcomes(outcomes: dict[str, Any]) -> str:
    """Formata os dados de career outcomes em Markdown."""
    parts: list[str] = []

    parts.append(f"**Fonte:** [{outcomes['source']}]({outcomes.get('source_url', '')})")
    if outcomes.get("pdf_url"):
        parts.append(f"  ([PDF direto]({outcomes['pdf_url']}))")
    parts.append(f"**Survey:** {outcomes.get('survey_timing', 'N/A')} | "
                 f"Response rate: {outcomes.get('response_rate', 'N/A')}")
    if outcomes.get("note"):
        parts.append(f"_{outcomes['note']}_")
    parts.append("")

    # Status geral
    status = outcomes.get("overall_status")
    if status:
        parts.append("### Destino dos graduados")
        parts.append(f"- **{status.get('employed', '?')}%** empregados")
        parts.append(f"- **{status.get('grad_school_or_fellowship', '?')}%** em grad school / fellowship")
        if status.get("military_volunteer_other"):
            parts.append(f"- **{status['military_volunteer_other']}%** serviço militar / voluntariado / outros")
        if status.get("actively_job_searching"):
            parts.append(f"- **{status['actively_job_searching']}%** ainda buscando emprego")
        if status.get("applying_to_grad_school"):
            parts.append(f"- **{status['applying_to_grad_school']}%** aplicando para grad school")
        parts.append("")

    # Salários
    salary = outcomes.get("salary")
    if salary:
        parts.append("### Salários (full-time, 6 meses pós-graduação)")
        parts.append(f"**Média geral:** ${salary['average_overall']:,} "
                     f"(amostra: {salary.get('sample_size', '?')} graduados)")
        parts.append("")
        parts.append("| Indústria | Média | Faixa |")
        parts.append("|-----------|------:|------:|")
        for entry in salary.get("by_industry", [])[:8]:
            low, high = entry.get("range", [0, 0])
            parts.append(f"| {entry['industry']} | ${entry['mean']:,} | "
                         f"${low:,}–${high:,} |")
        parts.append("")

    # Distribuição por indústria
    industry = outcomes.get("industry_distribution")
    if industry:
        parts.append("### Distribuição por indústria")
        for entry in industry[:10]:
            parts.append(f"- {entry['industry']}: **{entry['percent']}%**")
        parts.append("")

    # Localização
    location = outcomes.get("location_distribution")
    if location:
        parts.append("### Onde trabalham (localização)")
        for entry in location[:6]:
            parts.append(f"- {entry['region']}: **{entry['percent']}%**")
        parts.append("")

    # Experiential learning
    exp = outcomes.get("experiential_learning")
    if exp:
        parts.append("### Experiência durante a graduação")
        if exp.get("internship_participation"):
            parts.append(f"- **{exp['internship_participation']}%** fizeram pelo menos 1 estágio")
        if exp.get("research_participation"):
            parts.append(f"- **{exp['research_participation']}%** fizeram pesquisa")
        if exp.get("any_experiential_learning"):
            parts.append(f"- **{exp['any_experiential_learning']}%** participaram de experiential learning")
        if exp.get("deep_involvement_clubs_orgs"):
            parts.append(f"- **{exp['deep_involvement_clubs_orgs']}%** envolvimento profundo em clubes/orgs")
        parts.append("")

    return "\n".join(parts)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, stream=__import__("sys").stderr)
    outcomes = get_university_career_outcomes("Northwestern University")
    if outcomes:
        logging.info(format_career_outcomes(outcomes))
    else:
        logging.info("Nenhum dado de career outcomes configurado.")
