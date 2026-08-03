"""
Testes para funções de formatação/parsing de cada módulo (respostas mockadas).
Não faz chamadas de rede.
"""

from src.college_scorecard import format_school_summary
from src.orcid_client import OrcidProfile, OrcidWork, format_orcid_profile
from src.semantic_scholar import format_professor_research
from src.career_outcomes import format_career_outcomes
from src.university_opportunities import format_opportunities
from src.faculty_scraper import FacultyMember, format_faculty_list
from src.comparativo import generate_comparative_report


MOCK_SCHOOL = {
    "school.name": "Test University",
    "school.city": "Chicago",
    "school.state": "IL",
    "school.school_url": "www.test.edu",
    "latest.admissions.admission_rate.overall": 0.15,
    "latest.admissions.sat_scores.average.overall": 1450,
    "latest.admissions.act_scores.midpoint.cumulative": 33,
    "latest.cost.tuition.in_state": 55000,
    "latest.cost.tuition.out_of_state": 55000,
    "latest.cost.avg_net_price.overall": 25000,
    "latest.student.size": 8000,
    "latest.completion.completion_rate_4yr_150nt": 0.92,
    "latest.earnings.10_yrs_after_entry.median": 80000,
    "latest.aid.median_debt.completers.overall": 18000,
}


class TestFormatSchoolSummary:
    def test_basic_formatting(self):
        output = format_school_summary(MOCK_SCHOOL)
        assert "Test University" in output
        assert "Chicago" in output
        assert "15.0%" in output
        assert "1450" in output
        assert "$55,000" in output

    def test_missing_fields_show_nd(self):
        sparse = {"school.name": "Sparse U", "school.city": "", "school.state": ""}
        output = format_school_summary(sparse)
        assert "Sparse U" in output
        assert "N/D" in output


class TestFormatOrcidProfile:
    def test_with_enriched_works(self):
        profile = OrcidProfile(
            orcid_id="0000-0001-2345-6789",
            name="Jane Doe",
            affiliations=["CS, MIT"],
            works=[],
        )
        enriched = [
            {"title": "Paper A", "year": 2024, "venue": "NeurIPS", "citationCount": 50},
            {"title": "Paper B", "year": 2023, "venue": "ICML", "citationCount": 30},
        ]
        output = format_orcid_profile(profile, enriched)
        assert "Jane Doe" in output
        assert "0000-0001-2345-6789" in output
        assert "Paper A" in output
        assert "NeurIPS" in output
        assert "50 citações" in output

    def test_no_works(self):
        profile = OrcidProfile(
            orcid_id="0000-0000-0000-0000",
            name="Empty Prof",
            affiliations=[],
            works=[],
        )
        output = format_orcid_profile(profile)
        assert "Nenhum trabalho registrado" in output

    def test_orcid_works_without_enrichment(self):
        profile = OrcidProfile(
            orcid_id="0000-0001-0000-0000",
            name="John Smith",
            affiliations=["Dept X, Uni Y"],
            works=[
                OrcidWork(title="My Paper", year=2025, doi="10.1234/test", work_type="journal-article"),
            ],
        )
        output = format_orcid_profile(profile)
        assert "My Paper" in output
        assert "2025" in output


class TestFormatProfessorResearch:
    def test_basic(self):
        data = {
            "name": "Alice Prof",
            "affiliations": ["Stanford"],
            "h_index": 45,
            "citation_count": 12000,
            "paper_count": 150,
            "profile_url": "https://semanticscholar.org/author/123",
            "recent_papers": [
                {"title": "Cool Paper", "year": 2025, "venue": "AAAI", "citationCount": 10},
            ],
        }
        output = format_professor_research(data)
        assert "Alice Prof" in output
        assert "Stanford" in output
        assert "Cool Paper" in output
        assert "45" in output

    def test_none_returns_message(self):
        output = format_professor_research(None)
        assert "Nenhum resultado" in output


class TestFormatCareerOutcomes:
    def test_basic(self):
        data = {
            "source": "Test Report 2025",
            "source_url": "https://example.com",
            "pdf_url": "https://example.com/report.pdf",
            "survey_timing": "6 months post-graduation",
            "response_rate": "80%",
            "note": "Test note",
            "overall_status": {
                "employed": 70,
                "grad_school_or_fellowship": 25,
                "actively_job_searching": 5,
            },
            "salary": {
                "average_overall": 90000,
                "sample_size": 200,
                "by_industry": [
                    {"industry": "Tech", "mean": 120000, "range": [80000, 200000]},
                ],
            },
            "industry_distribution": [
                {"industry": "Tech", "percent": 30},
            ],
            "location_distribution": [
                {"region": "California", "percent": 25},
            ],
            "experiential_learning": {
                "internship_participation": 75,
                "research_participation": 60,
            },
        }
        output = format_career_outcomes(data)
        assert "Test Report 2025" in output
        assert "70%" in output
        assert "$90,000" in output
        assert "Tech" in output
        assert "California" in output


class TestFormatOpportunities:
    def test_basic(self):
        opps = {
            "incubators_accelerators": [
                {"name": "Test Incubator", "description": "An incubator", "url": "https://example.com"}
            ],
            "competitions": [
                {"name": "Hackathon X", "description": "Annual hack", "url": ""}
            ],
        }
        output = format_opportunities(opps)
        assert "Test Incubator" in output
        assert "Hackathon X" in output

    def test_empty_returns_message(self):
        output = format_opportunities({})
        assert "Nenhuma oportunidade" in output


class TestFormatFacultyList:
    def test_basic(self):
        members = [
            FacultyMember(name="Dr. Test", title="Professor", research_areas="AI", email="test@uni.edu", profile_url="https://uni.edu/test"),
        ]
        output = format_faculty_list(members)
        assert "Dr. Test" in output
        assert "Professor" in output
        assert "AI" in output

    def test_empty(self):
        output = format_faculty_list([])
        assert "Nenhum professor" in output
