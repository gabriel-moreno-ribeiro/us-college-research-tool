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
