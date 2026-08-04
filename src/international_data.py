"""
International admissions data, English requirements, and visa/founder pathways.

These functions generate structured queries and known data points for
international applicants. Since most data isn't available via a single API,
the tools combine:
1. Known institutional data (Common Data Set fields, IPEDS)
2. Web search queries for the model to execute via Exa/Firecrawl
3. Structured output format with provenance on every field
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProvenancedValue:
    value: Any
    source_url: str | None = None
    source_type: str = "unknown"  # official | unofficial | estimated
    confidence: str = "low"  # high | medium | low
    as_of: str | None = None
    caveat: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {"value": self.value, "source_type": self.source_type, "confidence": self.confidence}
        if self.source_url:
            d["source_url"] = self.source_url
        if self.as_of:
            d["as_of"] = self.as_of
        if self.caveat:
            d["caveat"] = self.caveat
        return d


# Known institutional policies (manually curated, high confidence)
KNOWN_POLICIES: dict[str, dict[str, Any]] = {
    "northwestern university": {
        "need_blind_international": False,
        "need_blind_policy": ProvenancedValue(
            value="need-aware",
            source_url="https://undergradaid.northwestern.edu/aid-basics/international-students.html",
            source_type="official",
            confidence="high",
            caveat="Northwestern is need-aware for international applicants. Financial need may affect admission decisions.",
        ),
        "aid_first_year_only": ProvenancedValue(
            value=True,
            source_url="https://undergradaid.northwestern.edu/aid-basics/international-students.html",
            source_type="official",
            confidence="high",
            caveat="International students can ONLY apply for institutional aid during freshman admission. Transfer and continuing students are NOT eligible.",
        ),
        "css_profile_code": "1565",
        "international_office_email": "iss@northwestern.edu",
        "international_office_url": "https://www.northwestern.edu/international/",
        "admission_office_email": "ug-admission@northwestern.edu",
        "regional_admission_officer_region": "Latin America",
    },
}

# Standard English proficiency tests
ENGLISH_TESTS = ["TOEFL iBT", "IELTS Academic", "Duolingo English Test", "Cambridge C1/C2", "PTE Academic", "TOEFL Essentials"]


def get_international_search_queries(university_name: str, country: str | None = None) -> list[dict[str, str]]:
    """Generate web search queries for international admissions data."""
    queries = [
        {"query": f'"{university_name}" common data set', "purpose": "acceptance_rate_international"},
        {"query": f'"{university_name}" international students admissions statistics', "purpose": "international_stats"},
        {"query": f'"{university_name}" class profile international', "purpose": "class_composition"},
        {"query": f'site:{_guess_edu_domain(university_name)} international admission requirements', "purpose": "requirements"},
        {"query": f'"{university_name}" financial aid international students', "purpose": "aid_policy"},
        {"query": f'"{university_name}" IPEDS international enrollment', "purpose": "ipeds_data"},
    ]
    if country:
        queries.append({"query": f'"{university_name}" students from {country}', "purpose": f"students_from_{country.lower()}"})
        queries.append({"query": f'"{university_name}" {country} alumni community', "purpose": "country_community"})
    return queries


def get_english_requirement_queries(university_name: str) -> list[dict[str, str]]:
    """Generate queries for English proficiency requirements."""
    return [
        {"query": f'site:{_guess_edu_domain(university_name)} english proficiency requirements TOEFL IELTS', "purpose": "english_requirements"},
        {"query": f'"{university_name}" Duolingo English Test minimum score', "purpose": "duolingo_requirement"},
        {"query": f'"{university_name}" test optional SAT ACT policy 2025 2026', "purpose": "test_policy"},
        {"query": f'"{university_name}" english waiver international', "purpose": "waiver_policy"},
    ]


def get_visa_pathway_queries(university_name: str) -> list[dict[str, str]]:
    """Generate queries for visa and founder pathways."""
    return [
        {"query": f'"{university_name}" F-1 OPT STEM extension CIP code', "purpose": "opt_stem"},
        {"query": f'"{university_name}" international students entrepreneurship startup', "purpose": "founder_resources"},
        {"query": f'"{university_name}" international entrepreneur visa F-1 business', "purpose": "f1_business"},
        {"query": f'site:{_guess_edu_domain(university_name)} international services office', "purpose": "iso_contact"},
    ]


def build_international_admissions_response(
    university_name: str,
    country: str | None = None,
) -> dict[str, Any]:
    """Build the structured response for international admissions tool."""
    uni_key = university_name.strip().lower()
    known = KNOWN_POLICIES.get(uni_key, {})

    response: dict[str, Any] = {
        "university": university_name,
        "applicant_country": country,
        "data": {},
        "search_queries": get_international_search_queries(university_name, country),
        "instructions": (
            "Execute the search_queries using Exa or Firecrawl to find actual numbers. "
            "For each data point found, include source_url, source_type, and confidence. "
            "Record all URLs via record_sources for NotebookLM export."
        ),
    }

    # Add known curated data
    if known:
        data = response["data"]
        if "need_blind_policy" in known:
            policy = known["need_blind_policy"]
            data["need_blind_international"] = policy.to_dict() if isinstance(policy, ProvenancedValue) else policy
        if "aid_first_year_only" in known:
            policy = known["aid_first_year_only"]
            data["aid_first_year_only"] = policy.to_dict() if isinstance(policy, ProvenancedValue) else policy
        if "css_profile_code" in known:
            data["css_profile_code"] = known["css_profile_code"]
        if "international_office_email" in known:
            data["international_office"] = {
                "email": known.get("international_office_email"),
                "url": known.get("international_office_url"),
            }
        if "admission_office_email" in known:
            data["admission_office"] = {
                "email": known.get("admission_office_email"),
                "regional_officer_region": known.get("regional_admission_officer_region"),
            }

    # Template for expected fields (model fills via web search)
    response["expected_fields"] = {
        "international_acceptance_rate": {"type": "number", "note": "Rarely published officially. Check CDS Section C."},
        "international_percent_freshman": {"type": "number", "note": "From class profile or CDS"},
        "international_percent_total": {"type": "number", "note": "From IPEDS or CDS"},
        "countries_represented": {"type": "integer"},
        "students_from_country": {"type": "integer", "note": f"Students from {country}" if country else "N/A"},
        "need_blind_international": {"type": "boolean"},
        "aid_first_year_only": {"type": "boolean", "note": "CRITICAL: if true, student cannot apply for aid after freshman year"},
        "documents_required": {"type": "list", "examples": ["CSS Profile", "ISFAA", "Bank statement", "Tax return translation"]},
    }

    return response


def build_english_requirements_response(university_name: str, program: str | None = None) -> dict[str, Any]:
    """Build structured response for English proficiency requirements."""
    return {
        "university": university_name,
        "program": program,
        "search_queries": get_english_requirement_queries(university_name),
        "expected_fields": {
            "toefl_ibt": {"minimum_total": None, "minimum_sections": None, "note": "Check for section minimums"},
            "ielts_academic": {"minimum_overall": None, "minimum_bands": None},
            "duolingo": {"minimum": None},
            "cambridge": {"minimum_scale": None, "accepted_levels": ["C1 Advanced", "C2 Proficiency"]},
            "pte_academic": {"minimum": None},
            "toefl_essentials": {"minimum": None},
            "waiver_conditions": {
                "by_country": None,
                "by_curriculum_language": None,
                "by_years_english_instruction": None,
                "by_sat_verbal": None,
            },
            "test_status": {"required_recommended_optional": None, "valid_until": None},
            "superscore_policy": None,
            "institution_code_toefl": None,
            "score_send_deadline": None,
        },
        "sat_act_policy": {
            "status": None,  # test-optional | test-free | test-required
            "policy_valid_for_cycle": None,
            "search_queries": [
                {"query": f'"{university_name}" test optional 2025 2026 SAT ACT', "purpose": "test_policy"},
            ],
        },
        "instructions": (
            "Execute search_queries to find current requirements. "
            "Many universities publish a clear table on their admissions page. "
            "Check both the general admissions page and the international students page. "
            "Record all URLs via record_sources."
        ),
    }


def build_visa_pathways_response(university_name: str) -> dict[str, Any]:
    """Build structured response for visa and founder pathways."""
    return {
        "university": university_name,
        "search_queries": get_visa_pathway_queries(university_name),
        "general_f1_info": {
            "can_own_company": True,
            "can_own_company_caveat": "F-1 students can FORM and OWN a US company (LLC or Corp) and receive equity. "
                                      "However, they CANNOT perform productive work for the company (including unpaid) "
                                      "without employment authorization (CPT or OPT).",
            "source": "USCIS guidance + 8 CFR 214.2(f)",
            "ein_requirement": "A company needs an EIN (Employer Identification Number) to open bank accounts, "
                               "receive prize money from competitions, and operate. F-1 students can apply for an EIN "
                               "as a responsible party.",
            "competition_prizes": "Many university startup competitions (e.g., VentureCat) require winners to have "
                                  "a US-registered entity with EIN to receive prize money. International students "
                                  "should form the entity BEFORE the competition.",
        },
        "opt_stem_info": {
            "standard_opt_months": 12,
            "stem_extension_months": 24,
            "total_with_stem": 36,
            "note": "ECE (CIP 14.1001) is on the STEM Designated Degree Program list. "
                    "Verify the specific CIP code for the university's program.",
            "cip_lookup_url": "https://studyinthestates.dhs.gov/stem-opt-hub/additional-resources/eligible-cip-codes",
        },
        "cpt_info": {
            "typical_availability": "After completing one full academic year (9 months)",
            "note": "Some universities allow CPT in first year for programs requiring it. Check with DSO.",
            "can_work_at_own_startup": "Only with CPT authorization AND if the work is directly related to major "
                                       "AND is part of a curricular requirement (internship course).",
        },
        "post_graduation_paths": [
            {"visa": "H-1B", "note": "Cap-subject (lottery). University-employed H-1B is cap-exempt."},
            {"visa": "O-1A", "note": "Extraordinary ability. Strong for founders with publications, patents, or awards."},
            {"visa": "International Entrepreneur Rule", "note": "Parole for founders with significant US investment or government grants. Reinstated 2021."},
            {"visa": "EB-1A/EB-2 NIW", "note": "Green card paths for extraordinary ability or national interest."},
        ],
        "university_specific_queries": get_visa_pathway_queries(university_name),
        "expected_fields": {
            "international_services_office": {"email": None, "url": None, "phone": None},
            "legal_resources_for_founders": None,
            "startup_visa_clinic": None,
            "entrepreneur_in_residence_program": None,
        },
        "disclaimer": "This is informational only, NOT legal advice. Immigration law changes frequently. "
                      "Always consult with a qualified immigration attorney and the university's DSO.",
        "instructions": (
            "Execute university_specific_queries to find this university's specific resources "
            "for international founders. Look for: legal clinics, immigration workshops, "
            "entrepreneurship office support for internationals. Record all URLs via record_sources."
        ),
    }


def _guess_edu_domain(university_name: str) -> str:
    """Guess the .edu domain from university name (heuristic)."""
    name = university_name.lower().strip()
    replacements = {
        "northwestern university": "northwestern.edu",
        "massachusetts institute of technology": "mit.edu",
        "stanford university": "stanford.edu",
        "carnegie mellon university": "cmu.edu",
        "georgia institute of technology": "gatech.edu",
        "university of michigan": "umich.edu",
        "university of california, berkeley": "berkeley.edu",
        "california institute of technology": "caltech.edu",
        "university of illinois urbana-champaign": "illinois.edu",
        "cornell university": "cornell.edu",
        "purdue university": "purdue.edu",
    }
    if name in replacements:
        return replacements[name]
    parts = name.replace("university of ", "").replace("university", "").strip().split()
    if parts:
        return f"{parts[0]}.edu"
    return "university.edu"
