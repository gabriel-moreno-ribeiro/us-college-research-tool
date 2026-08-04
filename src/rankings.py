"""
University rankings data from THE, QS, US News, and others.

Since ranking sites actively block scraping, this module generates
targeted search queries and structures the expected output format.
The model executes searches via Exa/Firecrawl and fills the template.
"""
from __future__ import annotations

from typing import Any


RANKING_SOURCES = [
    {
        "name": "Times Higher Education (THE)",
        "type": "world",
        "url_pattern": "https://www.timeshighereducation.com/world-university-rankings",
        "methodology_summary": "Teaching (29.5%), Research environment (29%), Research quality (30%), Industry (4%), International outlook (7.5%)",
        "has_subject": True,
    },
    {
        "name": "QS World University Rankings",
        "type": "world",
        "url_pattern": "https://www.topuniversities.com/world-university-rankings",
        "methodology_summary": "Academic reputation (30%), Employer reputation (15%), Faculty/student ratio (10%), Citations (20%), International (15%), Sustainability (5%), Employment outcomes (5%)",
        "has_subject": True,
        "subject_note": "QS ranks 'Engineering - Electrical & Electronic' as its own category",
    },
    {
        "name": "U.S. News National Universities",
        "type": "national",
        "url_pattern": "https://www.usnews.com/best-colleges/rankings/national-universities",
        "methodology_summary": "Outcomes (40%), Faculty resources (20%), Expert opinion (20%), Financial resources (10%), Student excellence (7%), Alumni giving (3%)",
        "has_subject": True,
        "subject_note": "Separate ranking for 'Best Undergraduate Engineering Programs'",
    },
    {
        "name": "U.S. News Global Universities",
        "type": "world",
        "url_pattern": "https://www.usnews.com/education/best-global-universities/rankings",
        "methodology_summary": "Global research reputation (12.5%), Regional research reputation (12.5%), Publications (10%), Citations (7.5%), plus 10+ other indicators",
        "has_subject": True,
    },
    {
        "name": "ARWU (Shanghai Ranking)",
        "type": "world",
        "url_pattern": "https://www.shanghairanking.com/rankings/arwu",
        "methodology_summary": "Alumni Nobel/Fields (10%), Staff Nobel/Fields (20%), Highly Cited (20%), Nature/Science pubs (20%), Total pubs (20%), Per capita (10%)",
        "has_subject": True,
    },
    {
        "name": "CSRankings",
        "type": "subject_only",
        "url_pattern": "https://csrankings.org/",
        "methodology_summary": "Publication count in top venues (pure output metric, no surveys). Most respected in CS/ECE academic community.",
        "has_subject": True,
        "subject_note": "Only covers CS/ECE/adjacent fields. Based on DBLP publication data.",
    },
]


def get_rankings_search_queries(university_name: str, subject: str | None = None) -> list[dict[str, str]]:
    """Generate search queries for university rankings."""
    queries = [
        {"query": f'"{university_name}" world university ranking 2025 2026', "purpose": "general_ranking"},
        {"query": f'"{university_name}" US News national university ranking', "purpose": "usnews_national"},
        {"query": f'"{university_name}" QS world university ranking', "purpose": "qs_ranking"},
        {"query": f'"{university_name}" Times Higher Education ranking', "purpose": "the_ranking"},
    ]
    if subject:
        queries.extend([
            {"query": f'"{university_name}" "{subject}" ranking 2025', "purpose": f"subject_ranking_{subject}"},
            {"query": f'"{university_name}" best undergraduate engineering programs ranking', "purpose": "engineering_ranking"},
            {"query": f'QS "{subject}" university ranking "{university_name}"', "purpose": "qs_subject"},
        ])
        if "electric" in subject.lower() or "computer" in subject.lower() or "cs" in subject.lower():
            queries.append({"query": f'csrankings.org "{university_name}"', "purpose": "csrankings"})
    return queries


def build_rankings_response(university_name: str, subject: str | None = None) -> dict[str, Any]:
    """Build structured response template for rankings tool."""
    return {
        "university": university_name,
        "subject": subject,
        "search_queries": get_rankings_search_queries(university_name, subject),
        "ranking_sources": RANKING_SOURCES,
        "expected_output_format": {
            "rankings": [
                {
                    "source": "ranking source name",
                    "type": "world | national | subject",
                    "rank": "integer or range",
                    "year": "integer",
                    "subject": "null for overall, or subject name",
                    "source_url": "URL where rank was found",
                    "methodology_summary": "one-line from RANKING_SOURCES",
                    "history_5yr": [{"year": 2022, "rank": None}],  # if available
                }
            ],
        },
        "instructions": (
            "Execute search_queries to find current rankings. For each ranking found:\n"
            "1. Record the exact rank, year, and source URL\n"
            "2. Look for BOTH overall AND subject-specific rankings\n"
            "3. If historical data is visible (trend), capture 5 years\n"
            "4. If a ranking site blocks access, return status='UNAVAILABLE' with manual_url\n"
            "5. NEVER fabricate a ranking number. If unsure, omit.\n"
            "6. Record all URLs via record_sources."
        ),
        "caveats": [
            "Rankings use different methodologies and are NOT directly comparable",
            "Subject rankings are more relevant than overall for program-level decisions",
            f"For ECE specifically, QS 'Electrical & Electronic Engineering' and CSRankings are most informative",
            "A university strong overall may be weaker in a specific department and vice-versa",
        ],
    }
