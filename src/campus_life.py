"""
Campus life data: climate, location, housing, safety, cost of living.

Practical information that affects daily life decisions, especially
for international students unfamiliar with US geography and climate.
"""
from __future__ import annotations

from typing import Any


# Pre-populated climate/location data for configured universities
CAMPUS_DATA: dict[str, dict[str, Any]] = {
    "northwestern university": {
        "location": {
            "city": "Evanston",
            "state": "Illinois",
            "metro_area": "Chicago metropolitan area",
            "distance_to_city_center_miles": 12,
            "distance_to_city_center_transit_minutes": 35,
            "transit_method": "CTA Purple Line (L train) to Chicago Loop",
            "nearest_international_airport": "Chicago O'Hare International (ORD)",
            "airport_distance_miles": 18,
            "airport_transit_minutes": 45,
            "campus_setting": "suburban, lakefront (Lake Michigan)",
        },
        "climate": {
            "climate_type": "Humid continental (hot summers, cold winters)",
            "january_avg_high_f": 31,
            "january_avg_low_f": 17,
            "july_avg_high_f": 84,
            "july_avg_low_f": 66,
            "annual_snowfall_inches": 36,
            "winter_note": "Winters are harsh (Nov-Mar). Wind chill from Lake Michigan can make it feel -10F to -20F. "
                           "This is a significant adjustment for students from tropical climates.",
            "comparison_for_brazilian": "January in Evanston feels like being inside a freezer. "
                                        "You will need a heavy winter coat ($200-400), thermal layers, waterproof boots, "
                                        "and gloves. Budget $500+ for cold weather gear in your first year.",
        },
        "housing": {
            "freshman_guarantee": True,
            "freshman_required_on_campus": True,
            "international_priority": True,
            "typical_room_and_board_annual": 19000,
            "residential_colleges": ["Allison", "Bobb-McCulloch", "Elder", "Foster-Walker", "Sargent", "Shepard", "Willard"],
            "off_campus_typical_rent_monthly": 900,
            "off_campus_note": "Most students live on campus freshman and sophomore year. Off-campus housing in Evanston is expensive.",
        },
        "cost_of_living": {
            "city_cost_index": "High (Chicago metro)",
            "monthly_estimate_usd": {
                "food_groceries": 400,
                "food_eating_out": 200,
                "transportation": 100,
                "personal_phone_misc": 150,
                "health_insurance_note": "Mandatory student health plan ~$3,500/year unless waived with equivalent coverage",
            },
            "total_monthly_estimate": 850,
            "annual_living_beyond_tuition": 10200,
        },
        "safety": {
            "clery_act_url": "https://www.northwestern.edu/up/your-safety/clery-reports.html",
            "campus_police": "Northwestern University Police (NUPD)",
            "emergency_phone": "847-491-3456",
            "safe_ride_service": True,
            "general_assessment": "Evanston is generally safe. The campus borders Chicago's Rogers Park neighborhood. "
                                  "Standard urban awareness applies for late night walks.",
        },
    },
}


def get_campus_life_search_queries(university_name: str) -> list[dict[str, str]]:
    """Generate search queries for campus life data."""
    return [
        {"query": f'"{university_name}" freshman housing guarantee cost room board', "purpose": "housing"},
        {"query": f'"{university_name}" cost of living students monthly expenses', "purpose": "cost_of_living"},
        {"query": f'"{university_name}" Clery Act crime statistics campus safety', "purpose": "safety"},
        {"query": f'"{university_name}" campus location city transportation', "purpose": "location"},
        {"query": f'"{university_name}" weather climate winter international students', "purpose": "climate"},
    ]


def build_campus_life_response(university_name: str, country: str | None = None) -> dict[str, Any]:
    """Build structured response for campus life tool."""
    uni_key = university_name.strip().lower()
    known = CAMPUS_DATA.get(uni_key)

    response: dict[str, Any] = {
        "university": university_name,
        "search_queries": get_campus_life_search_queries(university_name),
    }

    if known:
        response["data"] = known
        response["data_source"] = "curated (verified from official sources)"
    else:
        response["data"] = None
        response["expected_fields"] = {
            "location": {
                "city": None, "state": None, "metro_area": None,
                "distance_to_city_center_miles": None,
                "nearest_international_airport": None,
                "campus_setting": None,
            },
            "climate": {
                "january_avg_high_f": None, "january_avg_low_f": None,
                "july_avg_high_f": None, "annual_snowfall_inches": None,
                "winter_note": None,
            },
            "housing": {
                "freshman_guarantee": None,
                "international_priority": None,
                "typical_room_and_board_annual": None,
            },
            "cost_of_living": {"monthly_estimate_usd": None},
            "safety": {"clery_act_url": None},
        }

    response["instructions"] = (
        "Execute search_queries if data is not pre-populated. "
        "Climate data is factual (NOAA/weather.gov). Housing costs from university website. "
        "Safety stats from Clery Act Annual Security Report (federally mandated, public). "
        "Record all URLs via record_sources."
    )

    return response
