"""
Gera relatório comparativo lado a lado para modo batch.

Puxa dados do College Scorecard de cada universidade e monta uma tabela Markdown.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from .college_scorecard import CollegeScorecardClient


def generate_comparative_report(
    university_names: list[str],
) -> str:
    """Gera tabela comparativa com dados do College Scorecard."""
    sc_client = CollegeScorecardClient()
    schools: list[tuple[str, dict[str, Any] | None]] = []

    for name in university_names:
        try:
            school = sc_client.get_by_exact_name(name)
            schools.append((name, school))
        except (ValueError, Exception) as e:
            schools.append((name, None))

    parts: list[str] = [
        f"# Comparativo de Universidades",
        f"_Gerado em {date.today().isoformat()}_\n",
    ]

    if not any(s for _, s in schools):
        parts.append("_Nenhuma universidade encontrada na College Scorecard._")
        return "\n".join(parts)

    # Build table
    headers = ["Métrica"] + [name for name, _ in schools]
    separator = [":---"] + ["---:" for _ in schools]

    rows: list[list[str]] = []

    def _get(school: dict | None, key: str, fmt: str = "") -> str:
        if not school:
            return "N/D"
        val = school.get(key)
        if val is None:
            return "N/D"
        if fmt == "pct":
            return f"{float(val) * 100:.1f}%"
        if fmt == "money":
            return f"${int(val):,}"
        if fmt == "int":
            return f"{int(val):,}"
        return str(val)

    rows.append(["**Localização**"] + [
        _get(s, "school.city") + ", " + _get(s, "school.state") for _, s in schools
    ])
    rows.append(["**Taxa de admissão**"] + [
        _get(s, "latest.admissions.admission_rate.overall", fmt="pct") for _, s in schools
    ])
    rows.append(["**SAT médio**"] + [
        _get(s, "latest.admissions.sat_scores.average.overall", fmt="int") for _, s in schools
    ])
    rows.append(["**ACT mediana**"] + [
        _get(s, "latest.admissions.act_scores.midpoint.cumulative", fmt="int") for _, s in schools
    ])
    rows.append(["**Mensalidade (out-of-state)**"] + [
        _get(s, "latest.cost.tuition.out_of_state", fmt="money") for _, s in schools
    ])
    rows.append(["**Preço líquido médio**"] + [
        _get(s, "latest.cost.avg_net_price.overall", fmt="money") for _, s in schools
    ])
    rows.append(["**Corpo discente**"] + [
        _get(s, "latest.student.size", fmt="int") for _, s in schools
    ])
    rows.append(["**Conclusão 4 anos**"] + [
        _get(s, "latest.completion.completion_rate_4yr_150nt", fmt="pct") for _, s in schools
    ])
    rows.append(["**Ganhos 10 anos pós-entrada**"] + [
        _get(s, "latest.earnings.10_yrs_after_entry.median", fmt="money") for _, s in schools
    ])
    rows.append(["**Dívida mediana**"] + [
        _get(s, "latest.aid.median_debt.completers.overall", fmt="money") for _, s in schools
    ])

    # Format as markdown table
    parts.append("| " + " | ".join(headers) + " |")
    parts.append("| " + " | ".join(separator) + " |")
    for row in rows:
        parts.append("| " + " | ".join(row) + " |")

    parts.append("")
    parts.append("---")
    parts.append("_Dados: College Scorecard API (U.S. Department of Education)_")

    return "\n".join(parts)
