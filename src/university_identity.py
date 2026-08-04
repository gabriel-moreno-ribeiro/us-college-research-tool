"""
University identity, culture, and qualitative data.

Covers: motto, mission, campus vibe, traditions, fun facts, arguments
to attend, student life (publications, honors, arts, sports), community
engagement (non-tech clubs, service, student government), student support
centers, and consolidated points of contact.
"""
from __future__ import annotations

from typing import Any


# --- Requirement 1: University Identity / Why This University ---

def get_university_identity_queries(university_name: str) -> list[dict[str, str]]:
    """Queries for motto, mission, culture, why attend."""
    domain = _guess_domain(university_name)
    return [
        {"query": f'site:{domain} mission statement motto values', "purpose": "mission_motto"},
        {"query": f'site:{domain} about why {_short(university_name)} undergraduate experience', "purpose": "why_attend"},
        {"query": f'"{university_name}" campus culture student experience vibe', "purpose": "campus_vibe"},
        {"query": f'"{university_name}" traditions unique things students love', "purpose": "traditions"},
        {"query": f'site:{domain} virtual tour campus video', "purpose": "virtual_tour"},
        {"query": f'"{university_name}" student testimonials why I chose', "purpose": "testimonials"},
        {"query": f'site:{domain} facts about {_short(university_name)}', "purpose": "facts_page"},
    ]


def build_university_identity_response(university_name: str) -> dict[str, Any]:
    return {
        "university": university_name,
        "search_queries": get_university_identity_queries(university_name),
        "expected_fields": {
            "motto": {"value": None, "source_url": None, "language": None},
            "mission_statement": None,
            "founded_year": None,
            "campus_type": None,
            "distinctive_strengths": [],
            "traditions": [],
            "student_testimonial_quotes": [],
            "virtual_tour_url": None,
            "campus_video_url": None,
            "reasons_to_attend": [],
            "what_makes_it_unique": None,
        },
        "instructions": (
            "Execute search_queries to find qualitative identity data. Focus on:\n"
            "1. Official motto and mission from the university's 'About' page\n"
            "2. Unique traditions and campus culture (from student blogs, official pages)\n"
            "3. Virtual tour or campus video link\n"
            "4. Arguments for 'Why this university?' that go beyond rankings\n"
            "Always include source_url for each piece of information.\n"
            "Record all URLs via record_sources."
        ),
    }


# --- Requirement 7: Interesting/Fun Facts ---

def get_fun_facts_queries(university_name: str) -> list[dict[str, str]]:
    domain = _guess_domain(university_name)
    return [
        {"query": f'"{university_name}" fun facts interesting trivia', "purpose": "fun_facts"},
        {"query": f'"{university_name}" famous alumni notable graduates', "purpose": "famous_alumni"},
        {"query": f'"{university_name}" firsts inventions discoveries originated', "purpose": "firsts"},
        {"query": f'site:{domain} history milestones timeline', "purpose": "history"},
        {"query": f'"{university_name}" mascot traditions quirky', "purpose": "mascot_traditions"},
    ]


def build_fun_facts_response(university_name: str) -> dict[str, Any]:
    return {
        "university": university_name,
        "search_queries": get_fun_facts_queries(university_name),
        "expected_fields": {
            "fun_facts": [],
            "famous_alumni": [],
            "historical_firsts": [],
            "mascot": {"name": None, "story": None},
            "campus_quirks": [],
            "notable_inventions_or_discoveries": [],
            "in_pop_culture": [],
        },
        "instructions": (
            "Execute search_queries for trivia and notable facts. Look for:\n"
            "1. Official 'Facts & Figures' or 'About' page on .edu site\n"
            "2. Famous alumni (Nobel laureates, founders, cultural figures)\n"
            "3. Things invented or discovered at this university\n"
            "4. Mascot story and traditions\n"
            "5. Pop culture references (movies filmed on campus, TV shows)\n"
            "Record all URLs via record_sources."
        ),
    }


# --- Requirement 5: Community Engagement ---

def get_community_engagement_queries(university_name: str) -> list[dict[str, str]]:
    domain = _guess_domain(university_name)
    return [
        {"query": f'site:{domain} student organizations clubs directory', "purpose": "clubs_directory"},
        {"query": f'site:{domain} community service volunteer civic engagement', "purpose": "community_service"},
        {"query": f'site:{domain} student government associated students', "purpose": "student_government"},
        {"query": f'site:{domain} events calendar campus activities', "purpose": "events"},
        {"query": f'"{university_name}" greek life fraternities sororities', "purpose": "greek_life"},
        {"query": f'site:{domain} cultural organizations multicultural student groups', "purpose": "cultural_orgs"},
    ]


def build_community_engagement_response(university_name: str) -> dict[str, Any]:
    return {
        "university": university_name,
        "search_queries": get_community_engagement_queries(university_name),
        "expected_fields": {
            "total_student_organizations": None,
            "clubs_directory_url": None,
            "notable_clubs": [],
            "community_service_programs": [],
            "volunteer_organizations": [],
            "student_government": {"name": None, "url": None},
            "events_calendar_url": None,
            "major_annual_events": [],
            "greek_life": {"available": None, "participation_rate": None, "url": None},
            "cultural_organizations": [],
            "religious_organizations": [],
        },
        "instructions": (
            "Execute search_queries to find community engagement info. Focus on:\n"
            "1. Official student organizations directory (total count + URL)\n"
            "2. Community service and civic engagement programs\n"
            "3. Student government structure\n"
            "4. Major annual campus events and traditions\n"
            "5. Greek life availability and participation rate\n"
            "Always get the direct URL to the clubs directory.\n"
            "Record all URLs via record_sources."
        ),
    }


# --- Requirement 6: Student Support / Diversity Centers ---

def get_student_support_queries(university_name: str) -> list[dict[str, str]]:
    domain = _guess_domain(university_name)
    return [
        {"query": f'site:{domain} international student services support office', "purpose": "international_support"},
        {"query": f'site:{domain} diversity equity inclusion multicultural center', "purpose": "diversity_center"},
        {"query": f'site:{domain} counseling mental health wellness', "purpose": "mental_health"},
        {"query": f'site:{domain} academic support tutoring writing center', "purpose": "academic_support"},
        {"query": f'site:{domain} disability accessibility services', "purpose": "disability_services"},
        {"query": f'site:{domain} first generation students support', "purpose": "first_gen"},
        {"query": f'site:{domain} LGBTQ resources center', "purpose": "lgbtq_resources"},
    ]


def build_student_support_response(university_name: str) -> dict[str, Any]:
    return {
        "university": university_name,
        "search_queries": get_student_support_queries(university_name),
        "expected_fields": {
            "international_student_services": {"name": None, "url": None, "services": []},
            "diversity_multicultural_center": {"name": None, "url": None},
            "counseling_services": {"name": None, "url": None, "free_sessions": None},
            "academic_support": {
                "tutoring": None,
                "writing_center": None,
                "academic_advising": None,
            },
            "disability_services": {"name": None, "url": None},
            "first_gen_program": {"name": None, "url": None},
            "lgbtq_resources": {"name": None, "url": None},
            "wellness_center": {"name": None, "url": None},
        },
        "instructions": (
            "Execute search_queries to find student support resources. Focus on:\n"
            "1. International student services (ongoing support, not just admissions)\n"
            "2. Multicultural/diversity center name and URL\n"
            "3. Counseling services availability\n"
            "4. Academic support resources (tutoring, writing center)\n"
            "5. Specific programs for underrepresented students\n"
            "Record all URLs via record_sources."
        ),
    }


# --- Requirement 8: Points of Contact & Info Sessions ---

def get_contacts_queries(university_name: str) -> list[dict[str, str]]:
    domain = _guess_domain(university_name)
    return [
        {"query": f'site:{domain} admissions visit campus tour schedule', "purpose": "campus_visit"},
        {"query": f'site:{domain} information session register virtual', "purpose": "info_sessions"},
        {"query": f'site:{domain} admissions contact email phone', "purpose": "admissions_contact"},
        {"query": f'site:{domain} student ambassador connect chat', "purpose": "student_ambassadors"},
        {"query": f'site:{domain} undergraduate admissions staff counselors', "purpose": "admission_counselors"},
        {"query": f'"{university_name}" open house admitted students day', "purpose": "open_house"},
    ]


def build_contacts_response(university_name: str) -> dict[str, Any]:
    return {
        "university": university_name,
        "search_queries": get_contacts_queries(university_name),
        "expected_fields": {
            "admissions_office": {"email": None, "phone": None, "address": None, "url": None},
            "campus_visit": {"url": None, "booking_link": None, "available_tours": []},
            "virtual_tour_url": None,
            "info_sessions": {"url": None, "schedule_link": None, "virtual_available": None},
            "open_house_dates": [],
            "student_ambassador_program": {"url": None, "how_to_connect": None},
            "regional_admission_counselor": {"for_region": None, "name": None, "email": None},
            "department_contacts": {"ece_department": None, "engineering_school": None},
            "financial_aid_office": {"email": None, "phone": None, "url": None},
            "international_office": {"email": None, "phone": None, "url": None},
        },
        "instructions": (
            "Execute search_queries to find contact and visit information. Focus on:\n"
            "1. Campus visit booking page (direct URL)\n"
            "2. Info session registration (virtual and in-person)\n"
            "3. Admissions office direct contact (email, phone)\n"
            "4. Student ambassador or peer connection program\n"
            "5. Regional admission counselor for applicant's region\n"
            "6. Department-specific contacts for intended major\n"
            "Record all URLs via record_sources."
        ),
    }


# --- Requirement 9: Student Life (publications, honors, arts, sports) ---

def get_student_life_queries(university_name: str) -> list[dict[str, str]]:
    domain = _guess_domain(university_name)
    return [
        {"query": f'site:{domain} student publications newspaper magazine journal', "purpose": "publications"},
        {"query": f'site:{domain} honors program college requirements', "purpose": "honors_program"},
        {"query": f'site:{domain} performing arts theater music dance', "purpose": "performing_arts"},
        {"query": f'site:{domain} recreation intramural sports club sports', "purpose": "sports"},
        {"query": f'site:{domain} study abroad programs engineering', "purpose": "study_abroad"},
        {"query": f'site:{domain} student media radio television film', "purpose": "student_media"},
        {"query": f'site:{domain} dining options meal plans restaurants', "purpose": "dining"},
    ]


def build_student_life_response(university_name: str) -> dict[str, Any]:
    return {
        "university": university_name,
        "search_queries": get_student_life_queries(university_name),
        "expected_fields": {
            "student_publications": [],
            "student_newspaper": {"name": None, "url": None},
            "honors_program": {"name": None, "url": None, "requirements": None, "benefits": None},
            "performing_arts": {"theater": None, "music": None, "dance": None, "url": None},
            "varsity_sports": {"division": None, "conference": None, "notable_teams": []},
            "club_sports": [],
            "intramural_sports": {"available": None, "url": None},
            "study_abroad": {"programs_count": None, "url": None, "engineering_specific": []},
            "student_media": {"radio": None, "tv": None, "online": None},
            "dining": {"meal_plan_required_freshman": None, "options_count": None, "url": None},
            "recreation_center": {"name": None, "url": None, "facilities": []},
        },
        "instructions": (
            "Execute search_queries to find student life information. Focus on:\n"
            "1. Student-run publications (newspaper, magazines, journals)\n"
            "2. Honors program name, URL, and entry requirements\n"
            "3. Performing arts and creative opportunities (especially non-audition)\n"
            "4. Sports (varsity division, club sports, intramurals)\n"
            "5. Study abroad programs available to engineering students\n"
            "6. Student media outlets (radio, TV, online)\n"
            "Record all URLs via record_sources."
        ),
    }


# --- Requirement 10: Location Exploration ---

def get_location_exploration_queries(university_name: str) -> list[dict[str, str]]:
    domain = _guess_domain(university_name)
    city = _guess_city(university_name)
    return [
        {"query": f'"{city}" things to do students college attractions', "purpose": "city_attractions"},
        {"query": f'"{city}" food restaurants best eats near {_short(university_name)}', "purpose": "food_scene"},
        {"query": f'"{city}" nightlife entertainment bars students', "purpose": "nightlife"},
        {"query": f'"{city}" outdoor activities parks nature hiking', "purpose": "outdoors"},
        {"query": f'"{city}" museums galleries cultural attractions', "purpose": "culture"},
        {"query": f'"{university_name}" neighborhood walkability off campus life', "purpose": "neighborhood"},
        {"query": f'"{city}" day trips weekend getaways from campus', "purpose": "day_trips"},
    ]


def build_location_exploration_response(university_name: str) -> dict[str, Any]:
    city = _guess_city(university_name)
    return {
        "university": university_name,
        "city": city,
        "search_queries": get_location_exploration_queries(university_name),
        "expected_fields": {
            "city_overview": None,
            "neighborhood_description": None,
            "walkability_score": None,
            "cultural_attractions": [],
            "museums_galleries": [],
            "food_and_restaurants": [],
            "nightlife_entertainment": [],
            "outdoor_activities": [],
            "day_trips": [],
            "student_hangout_spots": [],
            "public_transportation": {"system": None, "quality": None, "student_discount": None},
            "city_comparison_note": None,
        },
        "instructions": (
            "Execute search_queries to find city/location exploration info. Focus on:\n"
            "1. What the surrounding city/neighborhood is like for students\n"
            "2. Cultural attractions (museums, theaters, music venues)\n"
            "3. Food scene (restaurants, cafes near campus)\n"
            "4. Weekend activities and day trips\n"
            "5. Public transit and getting around without a car\n"
            "Look for student-oriented guides and blogs, not generic tourism.\n"
            "Record all URLs via record_sources."
        ),
    }


# --- Helpers ---

def _guess_domain(university_name: str) -> str:
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
        "rice university": "rice.edu",
        "duke university": "duke.edu",
        "university of pennsylvania": "upenn.edu",
        "columbia university": "columbia.edu",
        "brown university": "brown.edu",
        "dartmouth college": "dartmouth.edu",
        "yale university": "yale.edu",
        "harvard university": "harvard.edu",
        "princeton university": "princeton.edu",
        "university of southern california": "usc.edu",
    }
    return domains.get(name, f"{name.split()[0]}.edu")


def _short(university_name: str) -> str:
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
        "rice university": "Rice",
        "duke university": "Duke",
        "university of pennsylvania": "Penn",
        "columbia university": "Columbia",
        "brown university": "Brown",
        "harvard university": "Harvard",
        "yale university": "Yale",
        "princeton university": "Princeton",
    }
    return shorts.get(university_name.lower().strip(), university_name.split()[0])


def _guess_city(university_name: str) -> str:
    cities = {
        "northwestern university": "Evanston, IL (Chicago area)",
        "massachusetts institute of technology": "Cambridge, MA (Boston area)",
        "stanford university": "Stanford, CA (Bay Area)",
        "carnegie mellon university": "Pittsburgh, PA",
        "georgia institute of technology": "Atlanta, GA",
        "cornell university": "Ithaca, NY",
        "purdue university": "West Lafayette, IN",
        "university of michigan": "Ann Arbor, MI",
        "rice university": "Houston, TX",
        "duke university": "Durham, NC",
        "university of pennsylvania": "Philadelphia, PA",
        "columbia university": "New York, NY",
        "brown university": "Providence, RI",
        "harvard university": "Cambridge, MA",
        "yale university": "New Haven, CT",
        "princeton university": "Princeton, NJ",
        "university of southern california": "Los Angeles, CA",
    }
    return cities.get(university_name.lower().strip(), "Unknown")
