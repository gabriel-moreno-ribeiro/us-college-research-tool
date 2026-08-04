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


def get_application_calendar_queries(university_name: str) -> list[dict[str, str]]:
    """Generate search queries for full application calendar."""
    domain = _guess_edu_domain(university_name)
    return [
        {"query": f'site:{domain} undergraduate admissions deadlines dates calendar 2025 2026', "purpose": "official_calendar"},
        {"query": f'site:{domain} early decision early action deadline', "purpose": "early_deadlines"},
        {"query": f'site:{domain} regular decision deadline notification date', "purpose": "rd_deadline"},
        {"query": f'site:{domain} financial aid deadline CSS FAFSA international', "purpose": "aid_deadlines"},
        {"query": f'site:{domain} CSS Profile deadline institution code financial aid', "purpose": "css_profile_details"},
        {"query": f'site:{domain} scholarship deadlines merit award priority', "purpose": "scholarship_deadlines"},
        {"query": f'site:{domain} international scholarship application deadline', "purpose": "intl_scholarships"},
        {"query": f'"{university_name}" merit scholarship named awards criteria deadline', "purpose": "named_scholarships"},
        {"query": f'site:{domain} IDOC verification documents deadline', "purpose": "idoc_deadline"},
        {"query": f'site:{domain} admissions interview schedule availability', "purpose": "interview_window"},
        {"query": f'site:{domain} admitted students decision day commit deposit', "purpose": "commitment_deadline"},
        {"query": f'site:{domain} campus visit tour fall spring schedule', "purpose": "visit_windows"},
        {"query": f'site:{domain} orientation international student pre-arrival', "purpose": "orientation"},
        {"query": f'"{university_name}" admissions timeline step by step', "purpose": "timeline_overview"},
    ]


def build_application_calendar_response(university_name: str) -> dict[str, Any]:
    """Build structured response for the full application calendar/timeline."""
    return {
        "university": university_name,
        "search_queries": get_application_calendar_queries(university_name),
        "calendar_template": {
            "application_cycle": None,
            "milestones": [
                {
                    "phase": "Preparation (Summer before senior year)",
                    "months": "Jun-Aug",
                    "tasks": [
                        {"task": "Research university and finalize school list", "deadline": None},
                        {"task": "Start drafting supplemental essays", "deadline": None},
                        {"task": "Request letters of recommendation from teachers", "deadline": None, "note": "Ask before school year rush"},
                        {"task": "Register for standardized tests (if needed)", "deadline": None},
                        {"task": "Schedule campus visit or virtual tour", "deadline": None},
                    ],
                },
                {
                    "phase": "Early Applications (Fall)",
                    "months": "Sep-Nov",
                    "tasks": [
                        {"task": "Common App / Coalition App opens", "date": "Aug 1", "fixed": True},
                        {"task": "FAFSA opens", "date": "Oct 1", "fixed": True, "note": "Submit ASAP for priority consideration"},
                        {"task": "Finalize Early Decision / Early Action essays", "deadline": None},
                        {"task": "Submit ED/EA application", "deadline": None, "type": "ED/EA"},
                        {"task": "Send SAT/ACT scores (if applicable)", "deadline": None},
                        {"task": "Submit CSS Profile for financial aid (ED)", "deadline": None, "type": "financial"},
                        {"task": "Submit merit scholarship application (if separate)", "deadline": None, "type": "scholarship"},
                        {"task": "Submit IDOC supporting documents (if required by CSS)", "deadline": None, "type": "financial"},
                        {"task": "Interview availability window opens", "deadline": None},
                    ],
                },
                {
                    "phase": "Regular Decision (Winter)",
                    "months": "Dec-Jan",
                    "tasks": [
                        {"task": "ED decision notification", "date": None, "type": "decision"},
                        {"task": "Submit Regular Decision application", "deadline": None, "type": "RD"},
                        {"task": "Submit CSS Profile for financial aid (RD)", "deadline": None, "type": "financial"},
                        {"task": "Submit FAFSA (if applicable)", "deadline": None, "type": "financial"},
                        {"task": "Submit IDOC supporting documents (RD)", "deadline": None, "type": "financial"},
                        {"task": "Submit external scholarship applications (priority deadlines)", "deadline": None, "type": "scholarship"},
                        {"task": "Send mid-year school report", "deadline": None},
                        {"task": "Complete alumni interview (if offered)", "deadline": None},
                    ],
                },
                {
                    "phase": "Decisions & Commitment (Spring)",
                    "months": "Mar-May",
                    "tasks": [
                        {"task": "RD decision notification", "date": None, "type": "decision"},
                        {"task": "Financial aid award letter received", "date": None, "type": "financial"},
                        {"task": "Compare financial aid packages across schools", "deadline": None},
                        {"task": "Appeal financial aid if needed (submit documentation)", "deadline": None, "type": "financial"},
                        {"task": "Attend admitted student events / Wildcat Days", "date": None},
                        {"task": "Submit enrollment deposit", "deadline": None, "type": "commitment", "note": "Usually May 1"},
                        {"task": "Accept/decline financial aid offer", "deadline": None, "type": "financial"},
                        {"task": "Submit final transcript", "deadline": None},
                    ],
                },
                {
                    "phase": "Pre-Arrival (Summer after commitment)",
                    "months": "Jun-Aug",
                    "tasks": [
                        {"task": "Apply for F-1 visa (international students)", "deadline": None},
                        {"task": "Complete housing application", "deadline": None},
                        {"task": "Attend orientation / international student pre-orientation", "date": None},
                        {"task": "Register for classes", "deadline": None},
                        {"task": "Activate health insurance", "deadline": None},
                        {"task": "Move-in day", "date": None},
                    ],
                },
            ],
        },
        "key_dates_summary": {
            "ed1_deadline": None,
            "ed2_deadline": None,
            "ea_deadline": None,
            "rd_deadline": None,
            "financial_aid_priority_deadline": None,
            "international_aid_deadline": None,
            "css_profile_deadline_ed": None,
            "css_profile_deadline_rd": None,
            "fafsa_priority_deadline": None,
            "idoc_deadline_ed": None,
            "idoc_deadline_rd": None,
            "ed_notification": None,
            "rd_notification": None,
            "aid_award_notification": None,
            "aid_appeal_deadline": None,
            "commitment_deadline": None,
            "interview_window": {"start": None, "end": None},
            "campus_visit_window": {"fall": None, "spring": None},
            "orientation_date": None,
            "classes_start": None,
        },
        "scholarships_and_aid_deadlines": {
            "css_profile": {
                "institution_code": None,
                "deadline_ed": None,
                "deadline_rd": None,
                "url": None,
                "note": "CSS Profile is required at most private universities for institutional aid",
            },
            "fafsa": {
                "school_code": None,
                "priority_deadline": None,
                "final_deadline": None,
                "required_for_international": None,
                "note": "FAFSA is for US citizens/permanent residents. Internationals use CSS Profile only.",
            },
            "idoc": {
                "required": None,
                "deadline_ed": None,
                "deadline_rd": None,
                "documents_needed": [],
                "note": "IDOC = Institutional Documentation Service. Submits tax docs to College Board for CSS schools.",
            },
            "merit_scholarships": {
                "automatic_consideration": None,
                "separate_application_required": None,
                "deadline": None,
                "named_awards": [],
                "criteria": None,
                "available_to_internationals": None,
                "url": None,
            },
            "need_based_aid": {
                "deadline_ed": None,
                "deadline_rd": None,
                "international_deadline": None,
                "documents_required": [],
                "meets_full_demonstrated_need": None,
                "average_package": None,
            },
            "external_scholarships_to_consider": [
                {"name": "QuestBridge", "deadline": "Sep (for Match)", "note": "Full-ride for low-income students"},
                {"name": "Davis UWC Scholars", "deadline": "Varies", "note": "For UWC graduates only"},
                {"name": "Stamps Scholarship", "deadline": "Varies by school", "note": "Full tuition + stipend"},
            ],
            "aid_appeal_process": {
                "allowed": None,
                "deadline": None,
                "how_to_appeal": None,
                "what_to_include": "Changed circumstances documentation, competing offers",
            },
        },
        "international_specific_notes": [
            "Financial aid deadlines for internationals are often EARLIER than domestic deadlines",
            "CSS Profile (not FAFSA) is typically required for international aid",
            "Some schools have a SEPARATE international financial aid application or form",
            "IDOC may require non-US tax documents translated to English",
            "Merit scholarships may have different eligibility rules for international students",
            "Visa processing takes 2-4 months — apply immediately after receiving I-20",
            "Some interviews may not be available in all countries",
            "ED is binding — if admitted with insufficient aid, can request release (but risky)",
            "Need-aware schools may disadvantage internationals who apply for aid — research each school's policy",
        ],
        "instructions": (
            "Execute search_queries to fill in ALL dates in calendar_template, key_dates_summary, "
            "and scholarships_and_aid_deadlines. Find the official admissions AND financial aid pages. "
            "Dates change yearly — verify they are for the CURRENT application cycle (2025-2026). "
            "Pay special attention to:\n"
            "1. Whether the school offers ED1, ED2, EA, REA, or only RD\n"
            "2. CSS Profile deadline (often DIFFERENT for ED vs RD, and for internationals)\n"
            "3. IDOC deadline — many CSS schools require this separately\n"
            "4. Merit scholarship deadlines (some are automatic, some require separate app)\n"
            "5. International financial aid deadlines (often EARLIER than domestic)\n"
            "6. Whether the school meets 100% demonstrated need\n"
            "7. Decision notification dates (when applicant hears back)\n"
            "8. Financial aid award letter timeline\n"
            "9. Aid appeal deadline and process\n"
            "10. Interview availability period and how to schedule\n"
            "11. Admitted student events / visit days dates\n"
            "Present the final calendar CHRONOLOGICALLY with exact dates where found.\n"
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
