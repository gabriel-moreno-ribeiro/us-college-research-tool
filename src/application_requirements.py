"""
Application requirements and deadlines for university admissions.

Generates structured queries and templates for the model to fill
with data from university admissions pages.
"""
from __future__ import annotations

from typing import Any


def get_application_search_queries(university_name: str) -> list[dict[str, str]]:
    """Generate search queries for application requirements."""
    domain = _guess_edu_domain(university_name)
    return [
        {"query": f'site:{domain} undergraduate admission requirements international', "purpose": "admission_requirements"},
        {"query": f'site:{domain} application deadlines early decision regular', "purpose": "deadlines"},
        {"query": f'site:{domain} supplemental essays prompts', "purpose": "essays"},
        {"query": f'"{university_name}" common app supplemental essay prompts 2025 2026', "purpose": "essay_prompts_current"},
        {"query": f'site:{domain} letters of recommendation requirements', "purpose": "recommendations"},
        {"query": f'site:{domain} interview alumni admission', "purpose": "interview_policy"},
        {"query": f'site:{domain} application fee waiver international', "purpose": "fee_waiver"},
        {"query": f'"{university_name}" early decision acceptance rate', "purpose": "ed_rate"},
    ]


def get_curriculum_search_queries(university_name: str, program: str) -> list[dict[str, str]]:
    """Generate search queries for program curriculum."""
    domain = _guess_edu_domain(university_name)
    return [
        {"query": f'site:{domain} "{program}" major requirements curriculum', "purpose": "major_requirements"},
        {"query": f'site:{domain} "{program}" course sequence plan of study', "purpose": "course_sequence"},
        {"query": f'site:{domain} minor entrepreneurship requirements', "purpose": "entrepreneurship_minor"},
        {"query": f'site:{domain} dual degree combined major "{program}"', "purpose": "dual_degree"},
        {"query": f'site:{domain} undergraduate catalog "{program}"', "purpose": "catalog"},
        {"query": f'site:{domain} capstone senior design "{program}"', "purpose": "capstone"},
    ]


def build_application_requirements_response(university_name: str) -> dict[str, Any]:
    """Build structured response for application requirements."""
    return {
        "university": university_name,
        "search_queries": get_application_search_queries(university_name),
        "expected_fields": {
            "application_platform": {
                "type": None,  # common_app | coalition | both | proprietary
                "note": "Most selective schools accept Common App. Some also accept Coalition.",
            },
            "deadlines": {
                "early_decision_1": {"date": None, "binding": True},
                "early_decision_2": {"date": None, "binding": True},
                "early_action": {"date": None, "binding": False},
                "regular_decision": {"date": None},
                "financial_aid_deadline": {"date": None, "note": "Often different for internationals"},
                "css_profile_deadline": {"date": None},
                "score_send_deadline": {"date": None},
                "decision_release": {"date": None},
                "commitment_deadline": {"date": None, "note": "Usually May 1"},
            },
            "supplemental_essays": {
                "count": None,
                "prompts": [],
                "word_limits": [],
                "note": "The 'Why Us' essay is where research from this tool becomes competitive advantage",
            },
            "recommendations": {
                "required_count": None,
                "types": [],  # counselor, teacher (STEM), teacher (humanities), optional
                "additional_allowed": None,
            },
            "interview": {
                "available": None,  # yes | no | optional
                "format": None,  # alumni | admissions_staff | video
                "available_in_country": None,
                "how_to_sign_up": None,
            },
            "application_fee": {
                "amount_usd": None,
                "waiver_available": None,
                "waiver_for_internationals": None,
                "waiver_method": None,
            },
            "testing": {
                "sat_act_policy": None,  # required | test-optional | test-free
                "policy_valid_for_cycle": None,
                "sat_institution_code": None,
                "act_institution_code": None,
            },
            "portfolio_optional": {
                "accepted": None,
                "formats": [],  # github, personal website, art portfolio, research paper
            },
            "ed_advantage": {
                "note": "ED acceptance rate is often 2-3x higher than RD. Critical strategic decision.",
                "ed_rate_if_known": None,
                "rd_rate_if_known": None,
            },
        },
        "instructions": (
            "Execute search_queries to find current cycle requirements. "
            "Essay prompts change yearly - verify they're for the current cycle. "
            "Pay special attention to deadlines for international applicants "
            "(often earlier for financial aid). Record all URLs via record_sources."
        ),
    }


def build_curriculum_response(university_name: str, program: str) -> dict[str, Any]:
    """Build structured response for program curriculum."""
    return {
        "university": university_name,
        "program": program,
        "search_queries": get_curriculum_search_queries(university_name, program),
        "expected_fields": {
            "degree_type": None,  # BS, BA, BSE, etc.
            "total_credits_required": None,
            "major_credits": None,
            "general_education_credits": None,
            "free_electives": None,
            "core_courses": [],  # required courses with codes
            "elective_tracks": [],  # specialization options
            "capstone_project": {
                "required": None,
                "name": None,
                "description": None,
                "coordinator": None,
            },
            "dual_degree_options": [],
            "compatible_minors": [],
            "entrepreneurship_minor": {
                "available": None,
                "credits_required": None,
                "can_double_count": None,
                "declaration_deadline": None,
            },
            "study_abroad_options": [],
            "coop_internship": {
                "available": None,
                "required": None,
                "typical_timing": None,
            },
            "time_to_graduate": None,  # typical semesters
        },
        "instructions": (
            "Execute search_queries to find curriculum details from the official catalog. "
            "Focus on: total credits, required vs elective split, capstone project, "
            "and whether an entrepreneurship minor fits without extending graduation. "
            "Record all URLs via record_sources."
        ),
    }


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
        "university of michigan": "umich.edu",
        "university of illinois urbana-champaign": "illinois.edu",
        "california institute of technology": "caltech.edu",
    }
    return domains.get(name, f"{name.split()[0]}.edu")
