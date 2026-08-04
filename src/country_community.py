"""
Country community and alumni network discovery.

Finds student associations, alumni chapters, and scholarship programs
relevant to applicants from a specific country.
"""
from __future__ import annotations

from typing import Any


# Known organizations for Brazilian students in the US
BRAZIL_ORGANIZATIONS = {
    "brasa": {
        "name": "BRASA - Brazilian Student Association",
        "url": "https://www.gobrasa.org/",
        "description": "Largest network of Brazilian students in US/Canada. Has chapters at most major universities. Organizes the annual BRASA Summit.",
        "relevance": "First contact point for Brazilian applicants. Chapter leaders respond to DMs.",
    },
    "estudar_fora": {
        "name": "Estudar Fora (Fundacao Estudar)",
        "url": "https://www.estudarfora.org.br/",
        "description": "Brazilian organization that supports students applying to top universities abroad. Offers mentorship, content, and the Lemann Fellowship.",
        "relevance": "Free mentorship from alumni at target schools. Lemann Foundation partnership with select universities.",
    },
    "fundacao_lemann": {
        "name": "Fundacao Lemann",
        "url": "https://fundacaolemann.org.br/",
        "description": "Offers Lemann Fellowships at partner universities (Harvard, Stanford, Columbia, MIT, UCLA, Illinois). Check if this university is a partner.",
        "relevance": "Full or partial funding for Brazilian students at partner institutions.",
    },
    "education_usa": {
        "name": "EducationUSA Brasil",
        "url": "https://educationusa.state.gov/",
        "description": "US Department of State advising centers in Brazil. Free counseling on university applications, financial aid, and visa.",
        "relevance": "Official US government resource. Has offices in major Brazilian cities.",
    },
    "fulbright_brazil": {
        "name": "Comissao Fulbright Brasil",
        "url": "https://fulbright.org.br/",
        "description": "Fulbright scholarships for Brazilian students (primarily graduate, but some undergrad opportunities).",
        "relevance": "Prestigious scholarship. Primarily grad/research but worth checking undergrad eligibility.",
    },
    "ismart": {
        "name": "Ismart",
        "url": "https://ismart.org.br/",
        "description": "Brazilian NGO that identifies talented low-income students and supports their path to top universities, including abroad.",
        "relevance": "Full support pipeline from selection to university. Partners with some US institutions.",
    },
}


def get_country_community_queries(university_name: str, country: str = "Brazil") -> list[dict[str, str]]:
    """Generate search queries for country-specific community."""
    queries = []

    if country.lower() == "brazil":
        queries = [
            {"query": f'BRASA "{university_name}" OR "{_short_name(university_name)}"', "purpose": "brasa_chapter"},
            {"query": f'Brazilian Student Association "{university_name}"', "purpose": "brazilian_student_org"},
            {"query": f'"{university_name}" Brazilian students community', "purpose": "brazilian_community"},
            {"query": f'"{university_name}" Latin American Student Association', "purpose": "latam_org"},
            {"query": f'"{university_name}" alumni Brazil chapter', "purpose": "alumni_brazil"},
            {"query": f'"{university_name}" admission officer Latin America Brazil', "purpose": "regional_admission"},
            {"query": f'Fundacao Lemann "{university_name}" OR "{_short_name(university_name)}"', "purpose": "lemann_partnership"},
            {"query": f'"{university_name}" recruitment Brazil fair', "purpose": "recruitment_brazil"},
            {"query": f'site:{_guess_edu_domain(university_name)} student organizations international', "purpose": "student_orgs_page"},
        ]
    else:
        queries = [
            {"query": f'"{university_name}" {country} student association', "purpose": f"{country.lower()}_org"},
            {"query": f'"{university_name}" students from {country}', "purpose": "country_students"},
            {"query": f'"{university_name}" alumni {country}', "purpose": "alumni_country"},
            {"query": f'"{university_name}" admission officer {country}', "purpose": "regional_admission"},
        ]

    return queries


def build_country_community_response(university_name: str, country: str = "Brazil") -> dict[str, Any]:
    """Build structured response for country community tool."""
    response: dict[str, Any] = {
        "university": university_name,
        "country": country,
        "search_queries": get_country_community_queries(university_name, country),
        "expected_fields": {
            "student_organizations": [
                {"name": None, "url": None, "instagram": None, "contact_email": None, "leaders": None}
            ],
            "alumni_chapter_in_country": {"name": None, "url": None, "city": None, "contact": None},
            "regional_admission_officer": {"name": None, "email": None, "region_covered": None},
            "recruitment_events_in_country": [],
            "scholarship_programs": [],
            "alumni_interviews_in_country": {"available": None, "how_to_sign_up": None},
        },
        "instructions": (
            "Execute search_queries to find community resources. Prioritize:\n"
            "1. Official student org pages on the university's website\n"
            "2. Instagram/LinkedIn of student org leaders (public profiles only)\n"
            "3. Alumni chapter contact information\n"
            "4. Regional admission officer name and email\n"
            "Record all URLs via record_sources."
        ),
    }

    if country.lower() == "brazil":
        response["known_organizations"] = BRAZIL_ORGANIZATIONS
        response["note"] = (
            "Check if BRASA has a chapter at this university (gobrasa.org/chapters). "
            "Also check if Fundacao Lemann has a partnership with this institution. "
            "These are the two most impactful connections for a Brazilian applicant."
        )

    return response


def _short_name(university_name: str) -> str:
    """Get common short name for a university."""
    shorts = {
        "northwestern university": "Northwestern",
        "massachusetts institute of technology": "MIT",
        "stanford university": "Stanford",
        "carnegie mellon university": "CMU",
        "georgia institute of technology": "Georgia Tech",
        "university of michigan": "UMich",
        "california institute of technology": "Caltech",
        "cornell university": "Cornell",
        "purdue university": "Purdue",
    }
    return shorts.get(university_name.lower().strip(), university_name.split()[0])


def _guess_edu_domain(university_name: str) -> str:
    """Guess .edu domain."""
    name = university_name.lower().strip()
    domains = {
        "northwestern university": "northwestern.edu",
        "massachusetts institute of technology": "mit.edu",
        "stanford university": "stanford.edu",
        "carnegie mellon university": "cmu.edu",
        "georgia institute of technology": "gatech.edu",
        "cornell university": "cornell.edu",
        "purdue university": "purdue.edu",
    }
    return domains.get(name, f"{name.split()[0]}.edu")
