"""
Smoke test for the MCP server tools.

Tests the 10 acceptance criteria from the spec:
1. Server starts without env vars and reports NOT_CONFIGURED
2. search_university("northwestern") returns candidates with coverage info
3. get_university_overview for Northwestern returns data with provenance
4. get_university_overview("University College London") returns OUT_OF_SCOPE
5. get_professor_research("Karan Ahuja", "Northwestern") -> confidence high
6. get_professor_research("Emma Alexander", "Northwestern") -> confidence low with warning
7. list_faculty returns summarized and paginated (not 87 records at once)
8. Two calls to same tool: second is faster (cache)
9. match_professors_to_interests with "human-computer interaction" ranks correctly
10. draft_faculty_config produces selectors and sample

Additional:
11. stdout contains only valid JSON-RPC (no stray prints)

Run: python scripts/smoke_test_mcp.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the tools directly (bypassing MCP transport for testing)
from mcp_server.server import (
    compare_universities,
    draft_faculty_config,
    draft_opportunities,
    get_alumni_research_links,
    get_career_outcomes,
    get_opportunities,
    get_professor_research,
    get_university_overview,
    list_configured_departments,
    list_faculty,
    match_professors_to_interests,
    search_university,
    validate_faculty_config,
)

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"

results: list[tuple[str, bool, str]] = []


def test(name: str, passed: bool, detail: str = "") -> None:
    status = PASS if passed else FAIL
    results.append((name, passed, detail))
    print(f"  [{status}] {name}")
    if detail and not passed:
        print(f"         {detail}")


def dump_json(obj: Any, label: str = "") -> None:
    """Pretty-print a tool result for inspection."""
    if label:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"{'='*60}")
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


# Type alias
from typing import Any


def main() -> None:
    print("\n" + "="*60)
    print("  US College Research Tool — MCP Server Smoke Test")
    print("="*60 + "\n")

    has_api_key = bool(os.environ.get("COLLEGE_SCORECARD_API_KEY"))

    # ============================================================
    # Test 1: Server starts without env vars (NOT_CONFIGURED)
    # ============================================================
    print("\n[1] Server starts without scorecard key -> NOT_CONFIGURED")
    # Temporarily remove key to test (also prevent dotenv from reloading it)
    import mcp_server.server as srv
    original_key = os.environ.pop("COLLEGE_SCORECARD_API_KEY", None)
    srv._scorecard_api_key_present = None
    # Patch dotenv so it doesn't reload the key
    import unittest.mock
    with unittest.mock.patch("mcp_server.server.load_dotenv", lambda *a, **kw: None):
        result = search_university(query="MIT")
        test("search without API key returns NOT_CONFIGURED",
             result.get("status") == "NOT_CONFIGURED",
             f"Got: {result.get('status')}")
    # Restore
    if original_key:
        os.environ["COLLEGE_SCORECARD_API_KEY"] = original_key
    srv._scorecard_api_key_present = None

    # Re-detect key after restore (or from .env)
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    has_api_key = bool(os.environ.get("COLLEGE_SCORECARD_API_KEY"))

    if not has_api_key:
        print(f"\n  [{SKIP}] Tests 2-10 require COLLEGE_SCORECARD_API_KEY to be set.")
        print("  Set it in .env or as environment variable and re-run.")
        _print_summary()
        return

    # ============================================================
    # Test 2: search_university("northwestern") returns candidates
    # ============================================================
    print("\n[2] search_university('northwestern') -> candidates with coverage")
    result = search_university(query="northwestern")
    is_ok = result.get("status") == "OK"
    data = result.get("data")
    has_coverage = False
    if isinstance(data, list) and len(data) > 0:
        has_coverage = "has_faculty_config" in data[0]
    elif isinstance(data, dict):
        has_coverage = "has_faculty_config" in data
    test("search returns OK with candidates", is_ok, f"Status: {result.get('status')}")
    test("candidates include coverage info", has_coverage)
    dump_json(result, "search_university('northwestern')")

    # ============================================================
    # Test 3: get_university_overview (Northwestern) with provenance
    # ============================================================
    print("\n[3] get_university_overview('Northwestern University') -> provenance")
    result = get_university_overview(university_name="Northwestern University")
    is_ok = result.get("status") == "OK"
    has_source = False
    if is_ok and result.get("data", {}).get("metrics"):
        metric = result["data"]["metrics"].get("admission_rate", {})
        has_source = "source" in metric and "reference_year" in metric
    test("overview returns OK", is_ok, f"Status: {result.get('status')}")
    test("metrics have provenance (source + reference_year)", has_source)

    # ============================================================
    # Test 4: get_university_overview("University College London") -> OUT_OF_SCOPE
    # ============================================================
    print("\n[4] get_university_overview('University College London') -> OUT_OF_SCOPE")
    result = get_university_overview(university_name="University College London")
    test("UCL returns OUT_OF_SCOPE",
         result.get("status") == "OUT_OF_SCOPE",
         f"Got: {result.get('status')}, msg: {result.get('message', '')[:80]}")

    # ============================================================
    # Test 5: get_professor_research("Karan Ahuja") -> confidence high
    # ============================================================
    print("\n[5] get_professor_research('Karan Ahuja', 'Northwestern University')")
    result = get_professor_research(
        professor_name="Karan Ahuja",
        university_name="Northwestern University",
    )
    is_ok = result.get("status") == "OK"
    confidence = result.get("data", {}).get("identification_confidence", "")
    test("Karan Ahuja found", is_ok, f"Status: {result.get('status')}")
    test("identification_confidence is 'high'", confidence == "high", f"Got: {confidence}")
    dump_json(result, "get_professor_research('Karan Ahuja') — RAW OUTPUT")

    # ============================================================
    # Test 6: get_professor_research("Emma Alexander") -> confidence low
    # ============================================================
    print("\n[6] get_professor_research('Emma Alexander', 'Northwestern University')")
    result = get_professor_research(
        professor_name="Emma Alexander",
        university_name="Northwestern University",
    )
    is_ok = result.get("status") == "OK"
    confidence = result.get("data", {}).get("identification_confidence", "")
    has_warning = bool(result.get("data", {}).get("warning"))
    test("Emma Alexander found", is_ok, f"Status: {result.get('status')}")
    test("identification_confidence is 'low'", confidence == "low", f"Got: {confidence}")
    test("has explicit homonym warning", has_warning)
    dump_json(result, "get_professor_research('Emma Alexander') — RAW OUTPUT")

    # ============================================================
    # Test 7: list_faculty returns paginated, not all at once
    # ============================================================
    print("\n[7] list_faculty('northwestern_cs') -> paginated")
    result = list_faculty(faculty_config_key="northwestern_cs")
    is_ok = result.get("status") == "OK"
    data = result.get("data", [])
    total = result.get("total", 0)
    test("list_faculty returns OK", is_ok, f"Status: {result.get('status')}")
    test("returns <= 20 items (paginated)", len(data) <= 20, f"Got {len(data)} items")
    test("reports total count", total > 0, f"Total: {total}")
    test("has_more or next_offset indicated", "has_more" in result or "next_offset" in result)

    # ============================================================
    # Test 8: Cache hit is faster on second call
    # ============================================================
    print("\n[8] Cache test: second call is faster")
    t1 = time.time()
    _ = get_university_overview(university_name="Northwestern University")
    elapsed1 = time.time() - t1

    t2 = time.time()
    result = get_university_overview(university_name="Northwestern University")
    elapsed2 = time.time() - t2

    test("second call is faster (cache hit)",
         elapsed2 < elapsed1 * 0.8 or elapsed2 < 0.5,
         f"1st: {elapsed1:.2f}s, 2nd: {elapsed2:.2f}s")
    test("result indicates from_cache",
         result.get("from_cache") is True,
         f"from_cache: {result.get('from_cache')}")

    # ============================================================
    # Test 9: match_professors_to_interests
    # ============================================================
    print("\n[9] match_professors_to_interests with 'human-computer interaction'")
    result = match_professors_to_interests(
        university_name="Northwestern University",
        faculty_config_key="northwestern_cs",
        interests=["human-computer interaction"],
        max_professors=5,
    )
    is_ok = result.get("status") == "OK"
    ranked = result.get("data", {}).get("ranked_professors", [])
    top_name = ranked[0]["name"] if ranked else ""

    has_reasons = bool(ranked and ranked[0].get("match_reasons"))
    test("match returns OK", is_ok, f"Status: {result.get('status')}")
    test("returns ranked professors", len(ranked) > 0, f"Got {len(ranked)}")
    test("top result has match_reasons explaining WHY", has_reasons,
         f"Reasons: {ranked[0].get('match_reasons') if ranked else 'none'}")
    # Note: We check if Karan Ahuja is in top 3 (HCI researcher at Northwestern)
    top_3_names = [r["name"] for r in ranked[:3]]
    test("Karan Ahuja in top 3 for HCI",
         "Karan Ahuja" in top_3_names,
         f"Top 3: {top_3_names}")

    # ============================================================
    # Test 10: draft_faculty_config
    # ============================================================
    print("\n[10] draft_faculty_config on a faculty page")
    # Use Northwestern CS faculty page (known to work)
    configs = json.loads(open(PROJECT_ROOT / "data" / "faculty_configs.json", encoding="utf-8").read())
    test_url = configs.get("northwestern_cs", {}).get("url", "")
    if test_url:
        result = draft_faculty_config(faculty_page_url=test_url)
        is_ok = result.get("status") == "OK"
        has_selectors = bool(result.get("data", {}).get("proposed_config", {}).get("selectors"))
        has_sample = bool(result.get("data", {}).get("sample_extracted"))
        test("draft_faculty_config returns OK", is_ok, f"Status: {result.get('status')}")
        test("proposed config has selectors", has_selectors)
        test("includes extraction sample for validation", has_sample)
    else:
        test("draft_faculty_config (skipped - no URL in config)", False, "No test URL")

    # ============================================================
    # Test 11: draft_opportunities — no web_content returns NOT_CONFIGURED
    # ============================================================
    print("\n[11] draft_opportunities with empty web_content -> NOT_CONFIGURED")
    result = draft_opportunities(
        university_name="Carnegie Mellon University",
        web_content=[],
    )
    test("draft_opportunities empty input returns NOT_CONFIGURED",
         result.get("status") == "NOT_CONFIGURED",
         f"Got: {result.get('status')}")
    test("includes suggestion on how to proceed",
         "suggestion" in result,
         f"Keys: {list(result.keys())}")

    # ============================================================
    # Test 12: draft_opportunities — rejects items without URL
    # ============================================================
    print("\n[12] draft_opportunities rejects items missing source URL")
    result = draft_opportunities(
        university_name="Carnegie Mellon University",
        web_content=[
            {"content": "Some program info but no url field"},
            {"url": "", "content": "Empty url"},
            {"url": "https://www.cmu.edu/swartz-center/", "content": ""},
        ],
    )
    test("all invalid items -> NOT_CONFIGURED",
         result.get("status") == "NOT_CONFIGURED",
         f"Got: {result.get('status')}")
    test("reports which items were rejected",
         "rejected" in result and len(result["rejected"]) == 3,
         f"Rejected: {result.get('rejected')}")

    # ============================================================
    # Test 13: draft_opportunities — successful extraction with domain classification
    # ============================================================
    print("\n[13] draft_opportunities with valid content -> proposal with source_url + extraction_basis")
    fake_edu_content = """# Swartz Center for Entrepreneurship

    The Swartz Center supports student entrepreneurs through mentorship,
    funding, and resources. Programs include the McGinnis Venture Competition
    and the Swartz Entrepreneurial Fellowship.

    ## McGinnis Venture Competition

    Annual startup competition with $100,000+ in prizes. Open to all CMU students.

    ## Summer Research Program

    Undergraduate research grants for summer projects in any department.
    Applications due February each year.
    """
    fake_third_party_content = """# Best Entrepreneurship Programs

    Carnegie Mellon ranks among the top schools for startup culture.
    Their hackathon attracts 500+ participants annually.
    """
    result = draft_opportunities(
        university_name="Carnegie Mellon University",
        web_content=[
            {"url": "https://www.cmu.edu/swartz-center/programs", "content": fake_edu_content},
            {"url": "https://www.niche.com/colleges/cmu/", "content": fake_third_party_content},
        ],
    )
    is_ok = result.get("status") == "OK"
    data = result.get("data", {})
    items_total = data.get("total_items", 0)
    proposed = data.get("proposed_opportunities", {})

    test("draft_opportunities returns OK with valid content", is_ok, f"Status: {result.get('status')}")
    test("extracts at least one opportunity", items_total > 0, f"Total: {items_total}")
    test("proposal is grouped by category", len(proposed) > 0, f"Categories: {list(proposed.keys())}")

    # Check that every item has source_url and extraction_basis
    all_items = [item for cat_items in proposed.values() for item in cat_items]
    all_have_source = all("source_url" in item for item in all_items)
    all_have_basis = all("extraction_basis" in item for item in all_items)
    test("every item has source_url", all_have_source)
    test("every item has extraction_basis", all_have_basis)

    # Check domain classification
    edu_items = [item for item in all_items if item.get("source_url", "").endswith(".edu/swartz-center/programs")]
    third_party_items = [item for item in all_items if "niche.com" in item.get("source_url", "")]
    if edu_items:
        test("edu domain classified as official_university_domain",
             edu_items[0].get("extraction_basis") == "official_university_domain",
             f"Got: {edu_items[0].get('extraction_basis')}")
    if third_party_items:
        test("niche.com classified as third_party",
             third_party_items[0].get("extraction_basis") == "third_party",
             f"Got: {third_party_items[0].get('extraction_basis')}")

    test("does NOT auto-save (proposal only)",
         "note" in data and "Do NOT save without human approval" in data.get("note", ""))

    # ============================================================
    # Test 14: stdout purity (bonus)
    # ============================================================
    print("\n[14] No stray stdout output (JSON-RPC safety)")
    # This test validates by the fact that we're running and all output went to
    # print() which in this test script goes to stderr/stdout in test mode.
    # The real validation is that server.py has no print() statements.
    import ast
    server_path = PROJECT_ROOT / "mcp_server" / "server.py"
    tree = ast.parse(server_path.read_text(encoding="utf-8"))
    has_print = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                has_print = True
                break
    test("server.py has no print() calls", not has_print)

    _print_summary()


def _print_summary() -> None:
    print("\n" + "="*60)
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    all_pass = passed == total
    status = PASS if all_pass else FAIL
    print(f"  [{status}] {passed}/{total} tests passed")
    print("="*60 + "\n")

    if not all_pass:
        print("  Failed tests:")
        for name, p, detail in results:
            if not p:
                print(f"    - {name}: {detail}")
        print()

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
