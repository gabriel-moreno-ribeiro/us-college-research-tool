"""
Módulo de pesquisa de ALUMNI.

Decisão de design importante: este módulo NÃO faz scraping automatizado do
LinkedIn. Isso violaria os Termos de Serviço da plataforma e, feito em escala
sobre pessoas reais, levanta problemas sérios de privacidade.

Em vez disso, este módulo gera diretamente as URLs corretas da ferramenta
OFICIAL "LinkedIn Alumni Tool", já pré-filtradas por área de interesse,
empresa, cargo, e/ou localização, para você (o usuário logado) navegar
manualmente e ver com seus próprios olhos onde os ex-alunos foram parar.

Isso é deliberado: é a forma de ter esse dado respeitando os termos de uso da
plataforma e a privacidade de terceiros.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

TARGET_COMPANIES_PATH = Path(__file__).parent.parent / "data" / "target_companies.json"


@dataclass
class AlumniQuery:
    university_linkedin_slug: str
    field_of_study: str | None = None
    company: str | None = None
    keywords: str | None = None
    location: str | None = None
    label: str | None = None


def build_alumni_tool_url(query: AlumniQuery) -> str:
    """
    Monta a URL da ferramenta oficial linkedin.com/school/<slug>/people/
    com os filtros aplicados via query params (mesmo formato que o próprio
    site usa quando você aplica filtros manualmente na UI).
    """
    base = f"https://www.linkedin.com/school/{query.university_linkedin_slug}/people/"
    params = []
    if query.field_of_study:
        params.append(f"fieldOfStudy={quote(query.field_of_study)}")
    if query.company:
        params.append(f"company={quote(query.company)}")
    if query.keywords:
        params.append(f"keywords={quote(query.keywords)}")
    if query.location:
        params.append(f"geoRegion={quote(query.location)}")
    if params:
        base += "?" + "&".join(params)
    return base


def find_linkedin_slug_hint(university_name: str) -> str:
    """
    Heurística simples para sugerir o slug (nem sempre bate 100%, sempre
    confira manualmente pesquisando a universidade no LinkedIn e copiando
    a URL real do /school/.../).
    """
    return university_name.strip().lower().replace(", ", "-").replace(" ", "-")


def load_target_companies() -> dict:
    with open(TARGET_COMPANIES_PATH, encoding="utf-8") as f:
        return json.load(f)


def generate_alumni_queries(
    slug: str,
    field_of_study: str | None = None,
) -> list[AlumniQuery]:
    """
    Gera um conjunto completo de links úteis para pesquisa de alumni,
    combinando filtros de empresa, cargo e localização.
    """
    config = load_target_companies()
    queries: list[AlumniQuery] = []

    # 1. Link geral por área de estudo
    if field_of_study:
        queries.append(AlumniQuery(
            university_linkedin_slug=slug,
            field_of_study=field_of_study,
            label=f"Todos alumni de {field_of_study}",
        ))

    # 2. Por empresa (big tech + startups + consulting + VCs)
    company_groups = [
        ("Big Tech", config.get("big_tech", [])),
        ("Startups & Aceleradoras", config.get("startups_accelerators", [])),
        ("Consulting & Finance", config.get("consulting_finance", [])),
        ("Venture Capital", config.get("vc_funds", [])),
    ]
    for group_name, companies in company_groups:
        for company in companies:
            queries.append(AlumniQuery(
                university_linkedin_slug=slug,
                field_of_study=field_of_study,
                company=company,
                label=f"{group_name} → {company}",
            ))

    # 3. Por cargo/senioridade
    for role in config.get("target_roles", []):
        queries.append(AlumniQuery(
            university_linkedin_slug=slug,
            field_of_study=field_of_study,
            keywords=role,
            label=f"Cargo: {role}",
        ))

    # 4. Por localização
    for location in config.get("target_locations", []):
        queries.append(AlumniQuery(
            university_linkedin_slug=slug,
            field_of_study=field_of_study,
            location=location,
            label=f"Localização: {location}",
        ))

    return queries


def format_alumni_links(queries: list[AlumniQuery]) -> str:
    """Formata os links agrupados por categoria."""
    lines = ["### Links para pesquisa manual de alumni (LinkedIn Alumni Tool)", ""]

    current_category = None
    for q in queries:
        label = q.label or ""

        if "→" in label:
            category = label.split("→")[0].strip()
        elif label.startswith("Cargo:"):
            category = "Por cargo / senioridade"
        elif label.startswith("Localização:"):
            category = "Por localização"
        elif label.startswith("Todos"):
            category = "Geral"
        else:
            category = "Outros"

        if category != current_category:
            if current_category is not None:
                lines.append("")
            lines.append(f"**{category}**")
            current_category = category

        url = build_alumni_tool_url(q)
        display = label.split("→")[-1].strip() if "→" in label else label.split(":")[-1].strip()
        lines.append(f"- [{display}]({url})")

    lines.append("")
    lines.append(
        "> Confira se o slug da universidade está correto abrindo o primeiro link — se "
        "não encontrar a página, pesquise a universidade direto no LinkedIn e copie a "
        "URL real que aparece em '/school/.../'."
    )
    lines.append(">")
    lines.append(
        "> Empresas e cargos-alvo são configuráveis em `data/target_companies.json`."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, stream=__import__("sys").stderr)
    slug = find_linkedin_slug_hint("Northwestern University")
    queries = generate_alumni_queries(slug, field_of_study="Computer Science")
    logging.info(format_alumni_links(queries))
