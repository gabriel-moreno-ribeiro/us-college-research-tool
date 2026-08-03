"""
Testes para src/alumni_research.py — módulo puro/determinístico (não usa rede).
"""

from src.alumni_research import (
    AlumniQuery,
    build_alumni_tool_url,
    find_linkedin_slug_hint,
    format_alumni_links,
    generate_alumni_queries,
)


class TestBuildAlumniToolUrl:
    def test_basic_slug_only(self):
        q = AlumniQuery(university_linkedin_slug="northwestern-university")
        url = build_alumni_tool_url(q)
        assert url == "https://www.linkedin.com/school/northwestern-university/people/"

    def test_with_field_of_study(self):
        q = AlumniQuery(
            university_linkedin_slug="northwestern-university",
            field_of_study="Computer Science",
        )
        url = build_alumni_tool_url(q)
        assert "fieldOfStudy=Computer%20Science" in url

    def test_with_company(self):
        q = AlumniQuery(
            university_linkedin_slug="mit",
            company="Google",
        )
        url = build_alumni_tool_url(q)
        assert "company=Google" in url

    def test_with_keywords(self):
        q = AlumniQuery(
            university_linkedin_slug="stanford-university",
            keywords="Software Engineer",
        )
        url = build_alumni_tool_url(q)
        assert "keywords=Software%20Engineer" in url

    def test_with_location(self):
        q = AlumniQuery(
            university_linkedin_slug="mit",
            location="San Francisco Bay Area",
        )
        url = build_alumni_tool_url(q)
        assert "geoRegion=San%20Francisco%20Bay%20Area" in url

    def test_multiple_params(self):
        q = AlumniQuery(
            university_linkedin_slug="northwestern-university",
            field_of_study="Computer Science",
            company="Meta",
            location="New York",
        )
        url = build_alumni_tool_url(q)
        assert "fieldOfStudy=" in url
        assert "company=Meta" in url
        assert "geoRegion=" in url


class TestFindLinkedinSlugHint:
    def test_simple_name(self):
        assert find_linkedin_slug_hint("Northwestern University") == "northwestern-university"

    def test_name_with_comma(self):
        assert find_linkedin_slug_hint("University of California, Berkeley") == "university-of-california-berkeley"

    def test_strips_whitespace(self):
        assert find_linkedin_slug_hint("  MIT  ") == "mit"


class TestGenerateAlumniQueries:
    def test_returns_queries(self):
        queries = generate_alumni_queries("northwestern-university", field_of_study="Computer Science")
        assert len(queries) > 0
        assert all(isinstance(q, AlumniQuery) for q in queries)

    def test_first_query_is_general_field(self):
        queries = generate_alumni_queries("northwestern-university", field_of_study="Computer Science")
        assert queries[0].field_of_study == "Computer Science"
        assert queries[0].company is None
        assert queries[0].keywords is None

    def test_no_field_of_study(self):
        queries = generate_alumni_queries("mit")
        for q in queries:
            assert q.field_of_study is None

    def test_all_use_same_slug(self):
        queries = generate_alumni_queries("stanford-university", field_of_study="EE")
        for q in queries:
            assert q.university_linkedin_slug == "stanford-university"


class TestFormatAlumniLinks:
    def test_produces_markdown(self):
        queries = [
            AlumniQuery(university_linkedin_slug="mit", field_of_study="CS", label="Todos alumni de CS"),
            AlumniQuery(university_linkedin_slug="mit", company="Google", label="Big Tech → Google"),
        ]
        output = format_alumni_links(queries)
        assert "linkedin.com/school/mit/people/" in output
        assert "Google" in output

    def test_empty_list(self):
        output = format_alumni_links([])
        assert "LinkedIn Alumni Tool" in output
