"""
Tests for new tools added in BLOCO 0-4.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def test_list_configured_departments_no_crash():
    """Regression: list_configured_departments crashed on _readme string entry."""
    from mcp_server.server import list_configured_departments
    result = list_configured_departments()
    assert result["status"] == "OK"
    assert isinstance(result["data"], list)
    for dept in result["data"]:
        assert "config_key" in dept
        assert "url" in dept
        assert isinstance(dept["url"], str)


def test_list_configured_departments_skips_readme():
    """The _readme key in faculty_configs.json should not appear in results."""
    from mcp_server.server import list_configured_departments
    result = list_configured_departments()
    keys = [d["config_key"] for d in result["data"]]
    assert "_readme" not in keys


def test_get_international_admissions_northwestern():
    """Northwestern should return known need-aware policy."""
    from mcp_server.server import get_international_admissions
    result = get_international_admissions("Northwestern University", "Brazil")
    assert result["status"] == "OK"
    data = result["data"]["data"]
    assert data["need_blind_international"]["value"] == "need-aware"
    assert data["aid_first_year_only"]["value"] is True
    assert data["css_profile_code"] == "1565"
    assert len(result["data"]["search_queries"]) >= 6


def test_get_international_admissions_unknown_university():
    """Unknown university should still return search queries."""
    from mcp_server.server import get_international_admissions
    result = get_international_admissions("Unknown University XYZ")
    assert result["status"] == "OK"
    assert len(result["data"]["search_queries"]) >= 4


def test_get_english_requirements():
    """Should return structured template with search queries."""
    from mcp_server.server import get_english_requirements
    result = get_english_requirements("Northwestern University", "ECE")
    assert result["status"] == "OK"
    assert "toefl_ibt" in result["data"]["expected_fields"]
    assert "ielts_academic" in result["data"]["expected_fields"]
    assert "duolingo" in result["data"]["expected_fields"]


def test_get_visa_and_founder_pathways():
    """Should return F-1 info and OPT/STEM OPT data."""
    from mcp_server.server import get_visa_and_founder_pathways
    result = get_visa_and_founder_pathways("Northwestern University")
    assert result["status"] == "OK"
    data = result["data"]
    assert data["general_f1_info"]["can_own_company"] is True
    assert data["opt_stem_info"]["total_with_stem"] == 36
    assert "disclaimer" in data


def test_get_rankings():
    """Should return ranking sources and search queries."""
    from mcp_server.server import get_rankings
    result = get_rankings("Northwestern University", "Electrical and Electronic Engineering")
    assert result["status"] == "OK"
    assert len(result["data"]["ranking_sources"]) >= 5
    assert len(result["data"]["search_queries"]) >= 6


def test_get_country_community_brazil():
    """Should return BRASA and other Brazilian org data."""
    from mcp_server.server import get_country_community
    result = get_country_community("Northwestern University", "Brazil")
    assert result["status"] == "OK"
    orgs = result["data"]["known_organizations"]
    assert "brasa" in orgs
    assert "estudar_fora" in orgs
    assert "fundacao_lemann" in orgs


def test_record_sources():
    """Should record URLs for NotebookLM export."""
    from mcp_server.server import record_sources
    result = record_sources([
        {"url": "https://example.com/test1", "title": "Test 1", "category": "web_search"},
        {"url": "https://example.com/test2", "title": "Test 2", "university": "Test U"},
        {"url": "", "title": "Empty URL should be skipped"},
    ])
    assert result["status"] == "OK"
    assert result["data"]["recorded"] == 2
    assert result["data"]["total_submitted"] == 3


# --- Tests for qualitative/student life tools ---

def test_get_university_identity():
    """Should return search queries and expected fields."""
    from mcp_server.server import get_university_identity
    result = get_university_identity("Northwestern University")
    assert result["status"] == "OK"
    assert len(result["data"]["search_queries"]) >= 5
    assert "motto" in result["data"]["expected_fields"]
    assert "traditions" in result["data"]["expected_fields"]
    assert "reasons_to_attend" in result["data"]["expected_fields"]


def test_get_fun_facts():
    """Should return search queries for trivia/facts."""
    from mcp_server.server import get_fun_facts
    result = get_fun_facts("Northwestern University")
    assert result["status"] == "OK"
    assert len(result["data"]["search_queries"]) >= 4
    assert "fun_facts" in result["data"]["expected_fields"]
    assert "famous_alumni" in result["data"]["expected_fields"]
    assert "mascot" in result["data"]["expected_fields"]


def test_get_community_engagement():
    """Should return clubs/service/events queries."""
    from mcp_server.server import get_community_engagement
    result = get_community_engagement("Northwestern University")
    assert result["status"] == "OK"
    assert len(result["data"]["search_queries"]) >= 5
    assert "clubs_directory_url" in result["data"]["expected_fields"]
    assert "greek_life" in result["data"]["expected_fields"]


def test_get_student_support():
    """Should return support centers queries."""
    from mcp_server.server import get_student_support
    result = get_student_support("Northwestern University")
    assert result["status"] == "OK"
    assert len(result["data"]["search_queries"]) >= 5
    assert "international_student_services" in result["data"]["expected_fields"]
    assert "counseling_services" in result["data"]["expected_fields"]


def test_get_contacts_and_visits():
    """Should return admissions/visit contact queries."""
    from mcp_server.server import get_contacts_and_visits
    result = get_contacts_and_visits("Northwestern University")
    assert result["status"] == "OK"
    assert len(result["data"]["search_queries"]) >= 4
    assert "admissions_office" in result["data"]["expected_fields"]
    assert "campus_visit" in result["data"]["expected_fields"]
    assert "info_sessions" in result["data"]["expected_fields"]


def test_get_student_life():
    """Should return student life queries."""
    from mcp_server.server import get_student_life
    result = get_student_life("Northwestern University")
    assert result["status"] == "OK"
    assert len(result["data"]["search_queries"]) >= 5
    assert "honors_program" in result["data"]["expected_fields"]
    assert "varsity_sports" in result["data"]["expected_fields"]
    assert "study_abroad" in result["data"]["expected_fields"]


def test_get_location_exploration():
    """Should return city/location queries with correct city."""
    from mcp_server.server import get_location_exploration
    result = get_location_exploration("Northwestern University")
    assert result["status"] == "OK"
    assert "Evanston" in result["data"]["city"]
    assert len(result["data"]["search_queries"]) >= 5
    assert "food_and_restaurants" in result["data"]["expected_fields"]
    assert "day_trips" in result["data"]["expected_fields"]


def test_get_application_calendar():
    """Should return chronological calendar with milestones and key dates."""
    from mcp_server.server import get_application_calendar
    result = get_application_calendar("Northwestern University")
    assert result["status"] == "OK"
    data = result["data"]
    assert len(data["search_queries"]) >= 10
    assert "calendar_template" in data
    milestones = data["calendar_template"]["milestones"]
    assert len(milestones) == 5
    assert milestones[0]["phase"].startswith("Preparation")
    assert "key_dates_summary" in data
    assert "ed1_deadline" in data["key_dates_summary"]
    assert "rd_deadline" in data["key_dates_summary"]
    assert "css_profile_deadline_ed" in data["key_dates_summary"]
    assert "idoc_deadline_ed" in data["key_dates_summary"]
    # Scholarship and aid deadlines section
    assert "scholarships_and_aid_deadlines" in data
    sched = data["scholarships_and_aid_deadlines"]
    assert "css_profile" in sched
    assert "fafsa" in sched
    assert "idoc" in sched
    assert "merit_scholarships" in sched
    assert "need_based_aid" in sched
    assert "external_scholarships_to_consider" in sched
    assert "aid_appeal_process" in sched
    assert len(sched["external_scholarships_to_consider"]) >= 2
    # International notes
    assert "international_specific_notes" in data
    assert len(data["international_specific_notes"]) >= 5


def test_new_tools_work_for_unknown_university():
    """All new tools should work for any university, not just configured ones."""
    from mcp_server.server import (
        get_university_identity, get_fun_facts, get_community_engagement,
        get_student_support, get_contacts_and_visits, get_student_life,
        get_location_exploration,
    )
    for tool_fn in [get_university_identity, get_fun_facts, get_community_engagement,
                    get_student_support, get_contacts_and_visits, get_student_life,
                    get_location_exploration]:
        result = tool_fn("Stanford University")
        assert result["status"] == "OK"
        assert "search_queries" in result["data"]
        assert len(result["data"]["search_queries"]) >= 4
