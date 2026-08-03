"""
Cliente para a College Scorecard API (U.S. Department of Education).

API oficial, gratuita, pública: https://collegescorecard.ed.gov/data/api-documentation/
Requer uma API key gratuita de https://api.data.gov/signup/

Retorna dados de custo, admissão, corpo discente, e resultados financeiros
pós-formatura (earnings) para +6.000 instituições dos EUA.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from . import cache
from .source_tracker import record_source

BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools.json"

# Campos úteis para quem está pesquisando pra undergrad.
# Documentação completa de campos: https://collegescorecard.ed.gov/data/data-dictionary/
DEFAULT_FIELDS = [
    "id",
    "school.name",
    "school.city",
    "school.state",
    "school.school_url",
    "latest.admissions.admission_rate.overall",
    "latest.admissions.sat_scores.average.overall",
    "latest.admissions.act_scores.midpoint.cumulative",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
    "latest.cost.avg_net_price.overall",
    "latest.student.size",
    "latest.completion.completion_rate_4yr_150nt",
    "latest.earnings.10_yrs_after_entry.median",
    "latest.earnings.6_yrs_after_entry.median",
    "latest.aid.median_debt.completers.overall",
]


@dataclass
class CollegeScorecardClient:
    api_key: str = ""
    session: requests.Session = field(default_factory=requests.Session)
    delay_seconds: float = 0.3

    def __post_init__(self) -> None:
        # If no explicit key provided, try environment variable
        if not self.api_key:
            self.api_key = os.environ.get("COLLEGE_SCORECARD_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "COLLEGE_SCORECARD_API_KEY não encontrada. "
                "Pegue uma key gratuita em https://api.data.gov/signup/ "
                "e coloque no arquivo .env (ver .env.example)."
            )

    def search_school(self, name: str, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Busca escolas por nome (busca parcial, case-insensitive)."""
        cache_key = f"search:{name.lower().strip()}"
        cached = cache.get("scorecard", cache_key, max_age_days=30)
        if cached is not None:
            return cached

        params = {
            "api_key": self.api_key,
            "school.name": name,
            "fields": ",".join(fields or DEFAULT_FIELDS),
            "per_page": 20,
        }
        try:
            resp = self.session.get(BASE_URL, params=params, timeout=20)
            resp.raise_for_status()
        except requests.Timeout:
            raise RuntimeError("College Scorecard API: timeout na requisição")
        except requests.HTTPError as e:
            raise RuntimeError(f"College Scorecard API: erro HTTP {e.response.status_code}")
        except requests.ConnectionError:
            raise RuntimeError("College Scorecard API: falha de conexão (sem internet?)")

        time.sleep(self.delay_seconds)
        try:
            results = resp.json().get("results", [])
        except (ValueError, KeyError):
            raise RuntimeError("College Scorecard API: resposta JSON inválida")

        # Track source for each school found
        for school in results:
            school_name = school.get("school.name")
            if school_name:
                record_source(
                    url="https://collegescorecard.ed.gov/",
                    title=f"College Scorecard - {school_name}",
                    university=school_name,
                    category="institutional_data"
                )

        cache.put("scorecard", cache_key, results)
        return results

    def get_by_exact_name(self, name: str, fields: list[str] | None = None) -> dict[str, Any] | None:
        """Retorna o primeiro resultado que bate exatamente (case-insensitive) com o nome."""
        results = self.search_school(name, fields=fields)
        for r in results:
            if r.get("school.name", "").strip().lower() == name.strip().lower():
                return r
        return results[0] if results else None

    def compare(self, names: list[str], fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Busca várias escolas de uma vez, útil para montar tabela comparativa."""
        out = []
        for name in names:
            school = self.get_by_exact_name(name, fields=fields)
            if school:
                out.append(school)
        return out


def format_school_summary(school: dict[str, Any]) -> str:
    """Formata um resultado da API em um bloco de texto legível (Markdown)."""
    name = school.get("school.name", "N/A")
    city = school.get("school.city", "")
    state = school.get("school.state", "")
    url = school.get("school.school_url", "")
    admit_rate = school.get("latest.admissions.admission_rate.overall")
    sat = school.get("latest.admissions.sat_scores.average.overall")
    act = school.get("latest.admissions.act_scores.midpoint.cumulative")
    tuition_in = school.get("latest.cost.tuition.in_state")
    tuition_out = school.get("latest.cost.tuition.out_of_state")
    net_price = school.get("latest.cost.avg_net_price.overall")
    size = school.get("latest.student.size")
    completion = school.get("latest.completion.completion_rate_4yr_150nt")
    earnings_10y = school.get("latest.earnings.10_yrs_after_entry.median")
    debt = school.get("latest.aid.median_debt.completers.overall")

    def pct(v: Any) -> str:
        return f"{v * 100:.1f}%" if isinstance(v, (int, float)) else "N/D"

    def usd(v: Any) -> str:
        return f"${v:,.0f}" if isinstance(v, (int, float)) else "N/D"

    return f"""### {name} ({city}, {state})
- Site: {url or 'N/D'}
- Taxa de admissão: {pct(admit_rate)}
- SAT médio: {sat or 'N/D'} | ACT (mediana): {act or 'N/D'}
- Mensalidade (in-state / out-of-state): {usd(tuition_in)} / {usd(tuition_out)}
- Preço líquido médio (com ajuda financeira): {usd(net_price)}
- Tamanho do corpo discente: {size or 'N/D'}
- Taxa de conclusão em 4 anos: {pct(completion)}
- Ganhos medianos 10 anos após entrada: {usd(earnings_10y)}
- Dívida mediana ao concluir: {usd(debt)}
"""


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, stream=__import__("sys").stderr)
    client = CollegeScorecardClient()
    school = client.get_by_exact_name("Massachusetts Institute of Technology")
    if school:
        logging.info(format_school_summary(school))
    else:
        logging.info("Escola não encontrada.")
