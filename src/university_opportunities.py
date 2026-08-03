"""
Módulo de oportunidades na universidade (incubadoras, pesquisa undergrad, clubes, etc.).

Lê dados curados de data/opportunities.json — cada bloco é pesquisado manualmente
nos sites oficiais da universidade.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OPPORTUNITIES_PATH = Path(__file__).parent.parent / "data" / "opportunities.json"


def load_opportunities() -> dict[str, Any]:
    with open(OPPORTUNITIES_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_university_opportunities(university_name: str) -> dict[str, Any] | None:
    """Retorna as oportunidades de uma universidade ou None se não configurada."""
    data = load_opportunities()
    key = university_name.strip().lower().replace(" ", "_").replace(",", "")
    return data.get(key)


def format_opportunities(opps: dict[str, Any]) -> str:
    """Formata as oportunidades em Markdown."""
    sections: list[str] = []

    # Incubadoras
    if opps.get("incubators_accelerators"):
        sections.append("### Incubadoras & Aceleradoras")
        for item in opps["incubators_accelerators"]:
            sections.append(f"**[{item['name']}]({item['url']})**" if item.get("url") else f"**{item['name']}**")
            sections.append(f"  {item['description']}")
            if item.get("programs"):
                for prog in item["programs"]:
                    sections.append(f"  - {prog}")
            sections.append("")

    # Centros de empreendedorismo
    if opps.get("entrepreneurship_centers"):
        sections.append("### Centros de Empreendedorismo")
        for item in opps["entrepreneurship_centers"]:
            sections.append(f"**[{item['name']}]({item['url']})**" if item.get("url") else f"**{item['name']}**")
            sections.append(f"  {item['description']}")
            if item.get("programs"):
                for prog in item["programs"]:
                    sections.append(f"  - {prog}")
            sections.append("")

    # Competições
    if opps.get("competitions"):
        sections.append("### Competições de Startup & Hackathons")
        for item in opps["competitions"]:
            link = f"[{item['name']}]({item['url']})" if item.get("url") else item["name"]
            sections.append(f"- **{link}** — {item['description']}")
        sections.append("")

    # Pesquisa undergrad
    if opps.get("undergrad_research"):
        sections.append("### Programas de Pesquisa para Undergrad")
        for item in opps["undergrad_research"]:
            link = f"[{item['name']}]({item['url']})" if item.get("url") else item["name"]
            sections.append(f"- **{link}** — {item['description']}")
        sections.append("")

    # Clubes técnicos
    if opps.get("student_clubs_tech"):
        sections.append("### Clubes & Organizações Técnicas")
        for item in opps["student_clubs_tech"]:
            if item.get("url"):
                sections.append(f"- **[{item['name']}]({item['url']})** — {item['description']}")
            else:
                sections.append(f"- **{item['name']}** — {item['description']}")
        sections.append("")

    # Career centers
    if opps.get("career_centers"):
        sections.append("### Centros de Carreira")
        for item in opps["career_centers"]:
            sections.append(f"**[{item['name']}]({item['url']})**" if item.get("url") else f"**{item['name']}**")
            sections.append(f"  {item['description']}")
            if item.get("programs"):
                for prog in item["programs"]:
                    sections.append(f"  - {prog}")
            sections.append("")

    if not sections:
        return "_Nenhuma oportunidade configurada para esta universidade._"

    return "\n".join(sections)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, stream=__import__("sys").stderr)
    opps = get_university_opportunities("Northwestern University")
    if opps:
        logging.info(format_opportunities(opps))
    else:
        logging.info("Nenhuma oportunidade configurada.")
